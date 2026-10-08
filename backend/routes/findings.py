from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.finding import Finding
from schemas.finding import FindingSchema, SuggestionSchema

router = APIRouter(prefix="/api/findings", tags=["Findings"])

@router.get("/{finding_id}", response_model=FindingSchema)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    """Retrieve details and suggestion for an individual finding."""
    f = db.query(Finding).filter(Finding.finding_id == finding_id).first()
    if not f:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found.")

    sug = None
    if f.suggestion:
        sug = SuggestionSchema(
            original_code=f.suggestion.original_code,
            corrected_code=f.suggestion.corrected_code,
            recommendation=f.suggestion.recommendation
        )

    return FindingSchema(
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
        suggestion=sug
    )
