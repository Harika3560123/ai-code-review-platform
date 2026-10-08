from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class Finding(Base):
    __tablename__ = "findings"

    finding_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("code_reviews.review_id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=True)
    issue_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Numeric(5, 2), nullable=False, default=1.0)
    sources = Column(JSON, nullable=True, default=list) # e.g. ["static", "llm"]

    review = relationship("CodeReview", back_populates="findings")
    suggestion = relationship("Suggestion", back_populates="finding", uselist=False, cascade="all, delete-orphan")
