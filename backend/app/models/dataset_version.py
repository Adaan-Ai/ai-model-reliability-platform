"""
SQLAlchemy Model: DatasetVersion
Maps to table `dataset_version` (Core Entity 4)
"""

from sqlalchemy import Column, Integer, String, BigInteger, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class DatasetVersion(Base):
    __tablename__ = "dataset_version"

    dataset_version_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    dataset_id = Column(Integer, ForeignKey("dataset.dataset_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    version_number = Column(String(30), nullable=False)
    record_count = Column(BigInteger, nullable=False)
    created_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version"),
    )

    # Relationships
    dataset = relationship("Dataset", back_populates="versions")
    quality_results = relationship("DataQualityResult", back_populates="dataset_version", cascade="all, delete-orphan")
    evaluations = relationship("EvaluationRun", back_populates="dataset_version")
