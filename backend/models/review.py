from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base

class CodeReview(Base):
    __tablename__ = "code_reviews"

    review_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=True)
    language = Column(String(50), nullable=False)
    source_code = Column(Text(length=4294967295), nullable=False) # LONGTEXT in MySQL
    overall_score = Column(Numeric(5, 2), nullable=False, default=100.0)
    
    # Detailed quality scores & counts
    security_score = Column(Numeric(5, 2), nullable=True, default=100.0)
    correctness_score = Column(Numeric(5, 2), nullable=True, default=100.0)
    maintainability_score = Column(Numeric(5, 2), nullable=True, default=100.0)
    style_score = Column(Numeric(5, 2), nullable=True, default=100.0)
    complexity_score = Column(Numeric(5, 2), nullable=True, default=100.0)
    metrics_summary = Column(JSON, nullable=True) # {critical: X, high: Y, medium: Z, low: W}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reviews")
    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")
