from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base

class Suggestion(Base):
    __tablename__ = "suggestions"

    suggestion_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    finding_id = Column(Integer, ForeignKey("findings.finding_id", ondelete="CASCADE"), nullable=False, unique=True)
    original_code = Column(Text, nullable=True)
    corrected_code = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)

    finding = relationship("Finding", back_populates="suggestion")
