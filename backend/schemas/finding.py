from typing import List, Optional
from pydantic import BaseModel, Field

class SuggestionSchema(BaseModel):
    original_code: Optional[str] = ""
    corrected_code: Optional[str] = ""
    recommendation: Optional[str] = ""

class FindingSchema(BaseModel):
    finding_id: Optional[int] = None
    line: Optional[int] = None
    line_number: Optional[int] = None
    issue_type: str
    severity: str # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title: str
    message: Optional[str] = ""
    explanation: Optional[str] = ""
    evidence: Optional[str] = ""
    confidence: float = 1.0
    sources: List[str] = Field(default_factory=lambda: ["static"])
    suggestion: Optional[SuggestionSchema] = None

    def model_post_init(self, __context):
        # Synchronize line and line_number
        if self.line is not None and self.line_number is None:
            self.line_number = self.line
        elif self.line_number is not None and self.line is None:
            self.line = self.line_number

class RawFinding(BaseModel):
    line: Optional[int] = 1
    issue_type: str = "code_quality"
    severity: str = "MEDIUM"
    title: str
    message: str = ""
    explanation: Optional[str] = ""
    evidence: Optional[str] = ""
    confidence: float = 0.8
    source: str = "static"
    suggestion: Optional[SuggestionSchema] = None
