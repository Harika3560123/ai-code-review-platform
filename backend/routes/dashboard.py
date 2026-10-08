from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from models.user import User
from models.review import CodeReview
from models.finding import Finding
from utils.security import get_optional_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/statistics")
def get_dashboard_statistics(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Provide aggregated review analytics, quality trends, and severity breakdowns."""
    query = db.query(CodeReview)
    if current_user:
        query = query.filter(CodeReview.user_id == current_user.user_id)

    total_reviews = query.count()
    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_score": 100.0,
            "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "issue_type_counts": {},
            "language_counts": {},
            "recent_reviews": []
        }

    # Average score
    avg_score_raw = query.with_entities(func.avg(CodeReview.overall_score)).scalar()
    avg_score = round(float(avg_score_raw or 100.0), 2)

    # Languages breakdown
    lang_breakdown = {}
    lang_results = query.with_entities(CodeReview.language, func.count(CodeReview.review_id)).group_by(CodeReview.language).all()
    for lang, cnt in lang_results:
        lang_breakdown[lang] = cnt

    # Finding severities and types
    review_ids = [r.review_id for r in query.with_entities(CodeReview.review_id).all()]
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    type_counts = {}

    if review_ids:
        finding_rows = db.query(Finding.severity, Finding.issue_type, func.count(Finding.finding_id))\
            .filter(Finding.review_id.in_(review_ids))\
            .group_by(Finding.severity, Finding.issue_type).all()

        for sev, itype, cnt in finding_rows:
            sev_key = (sev or "low").lower()
            if sev_key in sev_counts:
                sev_counts[sev_key] += cnt
            
            clean_type = (itype or "other").lower()
            type_counts[clean_type] = type_counts.get(clean_type, 0) + cnt

    # Recent reviews (top 5)
    recent = query.order_by(CodeReview.created_at.desc()).limit(5).all()
    recent_list = [
        {
            "review_id": r.review_id,
            "filename": r.filename,
            "language": r.language,
            "score": float(r.overall_score),
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for r in recent
    ]

    return {
        "total_reviews": total_reviews,
        "average_score": avg_score,
        "severity_counts": sev_counts,
        "issue_type_counts": type_counts,
        "language_counts": lang_breakdown,
        "recent_reviews": recent_list
    }
