import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user import User
from models.review import CodeReview
from models.finding import Finding
from models.suggestion import Suggestion
from schemas.review import AnalyzeRequest, ReviewResponse, ReviewHistoryItem, SummaryCounts, DimensionScores
from schemas.finding import FindingSchema, SuggestionSchema
from utils.security import get_optional_current_user, get_current_user
from utils.validators import validate_code_input, validate_uploaded_file
from services.language_detector import resolve_language
from services.parser import CodeParser
from services.static_analyzer import StaticAnalyzerService
from services.llm_analyzer import LLMAnalyzerService
from services.explanation_engine import ExplanationEngine
from services.finding_fusion import FindingFusionService
from services.fix_generator import FixGeneratorService
from services.scoring import ScoringService

logger = logging.getLogger("code_review.routes.review")
router = APIRouter(prefix="/api/review", tags=["Code Review"])

static_service = StaticAnalyzerService()
llm_service = LLMAnalyzerService()

def execute_review_pipeline(
    code: str,
    raw_language: Optional[str],
    filename: Optional[str],
    user: Optional[User],
    db: Session
) -> ReviewResponse:
    """Core analysis orchestrator executing parsing, static analysis, AI analysis, fusion, and scoring."""
    clean_code, validated_lang = validate_code_input(code, raw_language)
    detected_language = resolve_language(validated_lang, filename, clean_code)
    clean_filename = filename or f"snippet.{'py' if detected_language == 'python' else 'js' if detected_language == 'javascript' else 'java'}"

    # Step 1: AST Parsing and Structural Metrics
    syntax_findings = []
    if detected_language == "python":
        tree, syntax_findings, metrics = CodeParser.parse_python(clean_code)
    else:
        syntax_findings, metrics = CodeParser.parse_generic(clean_code, detected_language)

    # Step 2: Deterministic Static Analysis (Bandit, Pylint, Semgrep, ESLint)
    static_findings, analyzer_status = static_service.analyze(clean_code, detected_language)

    # Combine static and syntax findings
    all_raw_findings = list(syntax_findings) + list(static_findings)

    # Step 3: AI / LLM Analysis & Offline Local Fallback
    llm_findings = []
    if llm_service.is_configured():
        llm_findings, llm_msg = llm_service.analyze(clean_code, detected_language, all_raw_findings)
        analyzer_status["llm"] = llm_msg
    else:
        analyzer_status["llm"] = "LLM service is not configured. Deterministic local static analysis active."

    # If no LLM findings were produced (either offline or no API key), run local deterministic rules
    local_findings = ExplanationEngine.run_local_fallback_analysis(clean_code, detected_language)

    # Collect all findings for fusion
    candidates = all_raw_findings + llm_findings + local_findings

    # Step 4: Finding Fusion & Deduplication
    fused_findings = FindingFusionService.fuse_findings(candidates)

    # Step 5: Explainability Enrichment & Fix Generation
    enriched_findings: List[FindingSchema] = []
    for f in fused_findings:
        f_enriched = ExplanationEngine.enrich_explainability(f, clean_code)
        if not f_enriched.suggestion or not f_enriched.suggestion.corrected_code:
            fix_res = FixGeneratorService.generate_fix(clean_code, f_enriched, detected_language)
            f_enriched.suggestion = SuggestionSchema(
                original_code=fix_res.original_code,
                corrected_code=fix_res.corrected_code,
                recommendation=fix_res.recommendation
            )
        enriched_findings.append(f_enriched)

    # Step 6: Scoring Formula Execution
    scores, summary = ScoringService.calculate_scores_and_summary(enriched_findings, metrics)

    # Step 7: Database Persistence (Users & Reviews)
    # If no logged-in user, map to demo/guest user
    user_id = user.user_id if user else None
    if user_id is None:
        guest_user = db.query(User).filter(User.email == "guest@codereview.local").first()
        if not guest_user:
            guest_user = User(
                name="Guest Developer",
                email="guest@codereview.local",
                password_hash="guest_no_login_needed"
            )
            db.add(guest_user)
            db.commit()
            db.refresh(guest_user)
        user_id = guest_user.user_id

    review_record = CodeReview(
        user_id=user_id,
        filename=clean_filename,
        language=detected_language,
        source_code=clean_code,
        overall_score=scores.overall,
        security_score=scores.security,
        correctness_score=scores.correctness,
        maintainability_score=scores.maintainability,
        style_score=scores.style,
        complexity_score=scores.complexity,
        metrics_summary=summary.model_dump()
    )
    db.add(review_record)
    db.commit()
    db.refresh(review_record)

    # Save findings and suggestions
    for item in enriched_findings:
        finding_db = Finding(
            review_id=review_record.review_id,
            line_number=item.line or 1,
            issue_type=item.issue_type,
            severity=item.severity,
            title=item.title,
            message=item.message,
            explanation=item.explanation,
            evidence=item.evidence,
            confidence=item.confidence,
            sources=item.sources
        )
        db.add(finding_db)
        db.commit()
        db.refresh(finding_db)
        item.finding_id = finding_db.finding_id

        if item.suggestion:
            suggestion_db = Suggestion(
                finding_id=finding_db.finding_id,
                original_code=item.suggestion.original_code,
                corrected_code=item.suggestion.corrected_code,
                recommendation=item.suggestion.recommendation
            )
            db.add(suggestion_db)
    db.commit()

    return ReviewResponse(
        review_id=review_record.review_id,
        filename=clean_filename,
        language=detected_language,
        overall_score=scores.overall,
        scores=scores,
        summary=summary,
        issues=enriched_findings,
        analyzer_status=analyzer_status,
        created_at=review_record.created_at
    )


@router.post("/analyze", response_model=ReviewResponse)
def analyze_code(
    payload: AnalyzeRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Analyze code snippet submitted via text editor."""
    return execute_review_pipeline(
        code=payload.code,
        raw_language=payload.language,
        filename=payload.filename,
        user=current_user,
        db=db
    )


@router.post("/upload", response_model=ReviewResponse)
async def upload_code_file(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Analyze source code provided via file upload."""
    clean_filename, detected_lang = validate_uploaded_file(file)
    content_bytes = await file.read()
    try:
        code_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content must be UTF-8 encoded text."
        )

    chosen_lang = language or detected_lang
    return execute_review_pipeline(
        code=code_str,
        raw_language=chosen_lang,
        filename=clean_filename,
        user=current_user,
        db=db
    )


@router.get("/history", response_model=List[ReviewHistoryItem])
def get_review_history(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve review history for the authenticated user or recent reviews for guest."""
    query = db.query(CodeReview)
    if current_user:
        query = query.filter(CodeReview.user_id == current_user.user_id)
    
    reviews = query.order_by(CodeReview.created_at.desc()).limit(50).all()

    history_items = []
    for r in reviews:
        summary_dict = r.metrics_summary or {}
        summary = SummaryCounts(
            critical=summary_dict.get("critical", 0),
            high=summary_dict.get("high", 0),
            medium=summary_dict.get("medium", 0),
            low=summary_dict.get("low", 0),
            info=summary_dict.get("info", 0)
        )
        history_items.append(ReviewHistoryItem(
            review_id=r.review_id,
            filename=r.filename,
            language=r.language,
            overall_score=float(r.overall_score),
            summary=summary,
            created_at=r.created_at
        ))
    return history_items


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_by_id(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve complete review report and findings by review ID."""
    review = db.query(CodeReview).filter(CodeReview.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    summary_dict = review.metrics_summary or {}
    summary = SummaryCounts(
        critical=summary_dict.get("critical", 0),
        high=summary_dict.get("high", 0),
        medium=summary_dict.get("medium", 0),
        low=summary_dict.get("low", 0),
        info=summary_dict.get("info", 0)
    )

    scores = DimensionScores(
        overall=float(review.overall_score),
        security=float(review.security_score or 100.0),
        correctness=float(review.correctness_score or 100.0),
        maintainability=float(review.maintainability_score or 100.0),
        style=float(review.style_score or 100.0),
        complexity=float(review.complexity_score or 100.0)
    )

    issues: List[FindingSchema] = []
    for f in review.findings:
        sug_schema = None
        if f.suggestion:
            sug_schema = SuggestionSchema(
                original_code=f.suggestion.original_code,
                corrected_code=f.suggestion.corrected_code,
                recommendation=f.suggestion.recommendation
            )
        issues.append(FindingSchema(
            finding_id=f.finding_id,
            line=f.line_number,
            line_number=f.line_number,
            issue_type=f.issue_type,
            severity=f.severity,
            title=f.title,
            message=f.message,
            explanation=f.explanation,
            evidence=f.evidence,
            confidence=float(f.confidence),
            sources=f.sources or ["static"],
            suggestion=sug_schema
        ))

    return ReviewResponse(
        review_id=review.review_id,
        filename=review.filename,
        language=review.language,
        overall_score=float(review.overall_score),
        scores=scores,
        summary=summary,
        issues=issues,
        analyzer_status={"status": "loaded from database"},
        created_at=review.created_at
    )


@router.get("/{review_id}/findings", response_model=List[FindingSchema])
def get_findings_for_review(review_id: int, db: Session = Depends(get_db)):
    """Retrieve only the findings for a specific review."""
    review = db.query(CodeReview).filter(CodeReview.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    findings: List[FindingSchema] = []
    for f in review.findings:
        sug_schema = None
        if f.suggestion:
            sug_schema = SuggestionSchema(
                original_code=f.suggestion.original_code,
                corrected_code=f.suggestion.corrected_code,
                recommendation=f.suggestion.recommendation
            )
        findings.append(FindingSchema(
            finding_id=f.finding_id,
            line=f.line_number,
            line_number=f.line_number,
            issue_type=f.issue_type,
            severity=f.severity,
            title=f.title,
            message=f.message,
            explanation=f.explanation,
            evidence=f.evidence,
            confidence=float(f.confidence),
            sources=f.sources or ["static"],
            suggestion=sug_schema
        ))
    return findings
