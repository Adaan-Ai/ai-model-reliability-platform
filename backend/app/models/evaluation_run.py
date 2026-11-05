"""
SQLAlchemy Model: EvaluationRun
Maps to table `evaluation_run` (Core Entity 9)
Central entity connecting model version, dataset version, user, and evaluation outcomes.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_run"

    evaluation_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    model_version_id = Column(Integer, ForeignKey("model_version.model_version_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    dataset_version_id = Column(Integer, ForeignKey("dataset_version.dataset_version_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    executed_by = Column(Integer, ForeignKey("user.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    execution_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('COMPLETED', 'RUNNING', 'FAILED')", name="chk_eval_status_valid"),
    )

    # Relationships
    model_version = relationship("ModelVersion", back_populates="evaluations")
    dataset_version = relationship("DatasetVersion", back_populates="evaluations")
    executor = relationship("User", back_populates="evaluations")

    # One-to-one with evaluation_result
    result = relationship("EvaluationResult", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")

    # One-to-many with drift_detection
    drift_records = relationship("DriftDetection", back_populates="evaluation", cascade="all, delete-orphan")

    # One-to-one with reliability_score
    reliability = relationship("ReliabilityScore", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
