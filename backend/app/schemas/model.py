"""
Pydantic Schemas: AIModel and ModelVersion
"""

from datetime import date
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserRead

# --- Model Version Schemas ---
class ModelVersionBase(BaseModel):
    version_number: str
    algorithm: str  # Logistic Regression, Random Forest, Decision Tree

class ModelVersionCreate(ModelVersionBase):
    model_id: int
    created_date: date | None = None

class ModelVersionRead(ModelVersionBase):
    model_version_id: int
    model_id: int
    created_date: date
    model_config = ConfigDict(from_attributes=True)

class ModelVersionDetail(ModelVersionRead):
    model_name: str | None = None
    model_type: str | None = None
    evaluation_count: int = 0
    latest_accuracy: float | None = None
    latest_f1: float | None = None

# --- AI Model Schemas ---
class AIModelBase(BaseModel):
    model_name: str
    model_type: str  # Classification, Regression, etc.
    description: str | None = None
    owner_id: int

class AIModelCreate(AIModelBase):
    created_date: date | None = None

class AIModelUpdate(BaseModel):
    model_name: str | None = None
    model_type: str | None = None
    description: str | None = None
    owner_id: int | None = None

class AIModelRead(AIModelBase):
    model_id: int
    created_date: date
    owner: UserRead | None = None
    version_count: int = 0
    latest_version: str | None = None
    model_config = ConfigDict(from_attributes=True)

class AIModelDetail(AIModelRead):
    versions: list[ModelVersionRead] = []
