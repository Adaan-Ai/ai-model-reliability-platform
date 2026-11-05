"""
SQLAlchemy Model: User
Maps to table `user` (Core Entity 1)
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    role = Column(String(50), nullable=False)
    department = Column(String(100), nullable=False)

    # Relationships
    datasets = relationship("Dataset", back_populates="owner")
    models = relationship("AIModel", back_populates="owner")
    evaluations = relationship("EvaluationRun", back_populates="executor")
