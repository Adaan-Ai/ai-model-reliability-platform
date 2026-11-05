"""
SQLAlchemy Model: DataQualityResult
Maps to table `data_quality_result` (Core Entity 6)
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class DataQualityResult(Base):
    __tablename__ = "data_quality_result"

    quality_result_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    quality_check_id = Column(Integer, ForeignKey("data_quality_check.quality_check_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    dataset_version_id = Column(Integer, ForeignKey("dataset_version.dataset_version_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    score = Column(Numeric(5, 2), nullable=False)
    status = Column(String(20), nullable=False)
    execution_date = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="chk_quality_score_range"),
        CheckConstraint("status IN ('PASSED', 'FAILED', 'WARNING')", name="chk_quality_status_valid"),
    )

    # Relationships
    quality_check = relationship("DataQualityCheck", back_populates="results")
    dataset_version = relationship("DatasetVersion", back_populates="quality_results")
