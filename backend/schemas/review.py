from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from schemas.finding import FindingSchema

class AnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: Optional[str] = None
    filename: Optional[str] = None

class SummaryCounts(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

class DimensionScores(BaseModel):
    overall: float = 100.0
    security: float = 100.0
    correctness: float = 100.0
    maintainability: float = 100.0
    style: float = 100.0
    complexity: float = 100.0

class ReviewResponse(BaseModel):
    review_id: Optional[int] = None
    filename: Optional[str] = "code_snippet"
    language: str
    overall_score: float
    scores: DimensionScores
    summary: SummaryCounts
    issues: List[FindingSchema]
    analyzer_status: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewHistoryItem(BaseModel):
    review_id: int
    filename: Optional[str]
    language: str
    overall_score: float
    summary: SummaryCounts
    created_at: datetime

    class Config:
        from_attributes = True

class FixRequest(BaseModel):
    original_code: str
    finding: FindingSchema
    language: Optional[str] = "python"

class FixResponse(BaseModel):
    original_code: str
    corrected_code: str
    recommendation: str
    diff_unified: str
