"""
SQLAlchemy Model: EvaluationResult
Maps to table `evaluation_result` (Core Entity 10)
Stores consolidated classification performance metrics for an evaluation run.
"""

from sqlalchemy import Column, Integer, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class EvaluationResult(Base):
    __tablename__ = "evaluation_result"

    result_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluation_run.evaluation_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True, index=True)
    accuracy = Column(Numeric(5, 2), nullable=False)
    precision_score = Column(Numeric(5, 2), nullable=False)
    recall_score = Column(Numeric(5, 2), nullable=False)
    f1_score = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("accuracy BETWEEN 0 AND 100", name="chk_accuracy_range"),
        CheckConstraint("precision_score BETWEEN 0 AND 100", name="chk_precision_range"),
        CheckConstraint("recall_score BETWEEN 0 AND 100", name="chk_recall_range"),
        CheckConstraint("f1_score BETWEEN 0 AND 100", name="chk_f1_range"),
    )

    # Relationships
    evaluation = relationship("EvaluationRun", back_populates="result")
