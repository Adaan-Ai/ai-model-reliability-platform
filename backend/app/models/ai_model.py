"""
SQLAlchemy Model: AIModel
Maps to table `ai_model` (Core Entity 7)
"""

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AIModel(Base):
    __tablename__ = "ai_model"

    model_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    model_name = Column(String(150), nullable=False)
    model_type = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    created_date = Column(Date, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="models")
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")
