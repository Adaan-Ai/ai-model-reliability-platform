"""
SQLAlchemy Model: DataSource
Maps to table `data_source` (Core Entity 2)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class DataSource(Base):
    __tablename__ = "data_source"

    source_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    source_name = Column(String(150), nullable=False)
    source_type = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)

    # Relationships
    datasets = relationship("Dataset", back_populates="source")
