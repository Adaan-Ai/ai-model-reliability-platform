"""
SQLAlchemy Model: Dataset
Maps to table `dataset` (Core Entity 3)
"""

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Dataset(Base):
    __tablename__ = "dataset"

    dataset_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    dataset_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_source.source_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("user.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    created_date = Column(Date, nullable=False)

    # Relationships
    source = relationship("DataSource", back_populates="datasets")
    owner = relationship("User", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    quality_checks = relationship("DataQualityCheck", back_populates="dataset", cascade="all, delete-orphan")
