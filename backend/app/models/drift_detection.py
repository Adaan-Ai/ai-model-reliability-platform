"""
SQLAlchemy Model: DriftDetection
Maps to table `drift_detection` (Core Entity 11)
Stores statistical distribution shift measurements against baseline datasets.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class DriftDetection(Base):
    __tablename__ = "drift_detection"

    drift_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluation_run.evaluation_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    drift_score = Column(Numeric(6, 4), nullable=False)
    drift_status = Column(String(20), nullable=False)
    detected_date = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("drift_score >= 0", name="chk_drift_score_positive"),
        CheckConstraint("drift_status IN ('LOW', 'MEDIUM', 'HIGH')", name="chk_drift_status_valid"),
    )

    # Relationships
    evaluation = relationship("EvaluationRun", back_populates="drift_records")
