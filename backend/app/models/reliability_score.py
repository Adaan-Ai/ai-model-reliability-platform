"""
SQLAlchemy Model: ReliabilityScore
Maps to table `reliability_score` (Core Entity 12)
Stores holistic reliability index combining data quality, model metrics, and drift.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ReliabilityScore(Base):
    __tablename__ = "reliability_score"

    reliability_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluation_run.evaluation_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True, index=True)
    data_quality_score = Column(Numeric(5, 2), nullable=False)
    model_performance_score = Column(Numeric(5, 2), nullable=False)
    drift_score = Column(Numeric(5, 2), nullable=False)
    overall_score = Column(Numeric(5, 2), nullable=False)
    rating = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("data_quality_score BETWEEN 0 AND 100", name="chk_rel_dq_range"),
        CheckConstraint("model_performance_score BETWEEN 0 AND 100", name="chk_rel_perf_range"),
        CheckConstraint("drift_score BETWEEN 0 AND 100", name="chk_rel_drift_range"),
        CheckConstraint("overall_score BETWEEN 0 AND 100", name="chk_rel_overall_range"),
        CheckConstraint("rating IN ('LOW', 'MEDIUM', 'HIGH')", name="chk_rel_rating_valid"),
    )

    # Relationships
    evaluation = relationship("EvaluationRun", back_populates="reliability")
