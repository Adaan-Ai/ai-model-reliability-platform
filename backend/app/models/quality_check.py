"""
SQLAlchemy Model: DataQualityCheck
Maps to table `data_quality_check` (Core Entity 5)
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DataQualityCheck(Base):
    __tablename__ = "data_quality_check"

    quality_check_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    dataset_id = Column(Integer, ForeignKey("dataset.dataset_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    check_name = Column(String(150), nullable=False)
    check_type = Column(String(50), nullable=False)
    threshold = Column(Numeric(5, 2), nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="quality_checks")
    results = relationship("DataQualityResult", back_populates="quality_check", cascade="all, delete-orphan")
