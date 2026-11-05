"""
SQLAlchemy Model: ModelVersion
Maps to table `model_version` (Core Entity 8)
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ModelVersion(Base):
    __tablename__ = "model_version"

    model_version_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_model.model_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    version_number = Column(String(30), nullable=False)
    algorithm = Column(String(100), nullable=False)
    created_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("model_id", "version_number", name="uq_model_version"),
    )

    # Relationships
    model = relationship("AIModel", back_populates="versions")
    evaluations = relationship("EvaluationRun", back_populates="model_version")
