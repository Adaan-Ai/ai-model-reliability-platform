"""
Pydantic Schemas: EvaluationRun and EvaluationResult
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user import UserRead
from app.schemas.drift import DriftDetectionRead, FeatureDriftDetail
from app.schemas.reliability import ReliabilityScoreRead

# --- Evaluation Result Schemas ---
class EvaluationResultBase(BaseModel):
    accuracy: Decimal | float = Field(ge=0.0, le=100.0)
    precision_score: Decimal | float = Field(ge=0.0, le=100.0)
    recall_score: Decimal | float = Field(ge=0.0, le=100.0)
    f1_score: Decimal | float = Field(ge=0.0, le=100.0)

class EvaluationResultRead(EvaluationResultBase):
    result_id: int
    evaluation_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Evaluation Run Schemas ---
class EvaluationRunCreate(BaseModel):
    model_version_id: int
    dataset_version_id: int
    executed_by: int
    target_column: str
    feature_columns: list[str] | None = None  # None selects all non-target columns
    test_size: float = Field(default=0.2, ge=0.05, le=0.5)
    random_state: int = Field(default=42)

class EvaluationRunRead(BaseModel):
    evaluation_id: int
    model_version_id: int
    dataset_version_id: int
    executed_by: int
    execution_date: datetime
    status: str  # COMPLETED, RUNNING, FAILED
    model_name: str | None = None
    model_version_number: str | None = None
    algorithm: str | None = None
    dataset_name: str | None = None
    dataset_version_number: str | None = None
    executor: UserRead | None = None
    result: EvaluationResultRead | None = None
    drift: DriftDetectionRead | None = None
    reliability: ReliabilityScoreRead | None = None
    model_config = ConfigDict(from_attributes=True)

class EvaluationRunDetail(EvaluationRunRead):
    confusion_matrix: list[list[int]] | None = None
    class_labels: list[str] | None = None
    classification_report: dict | None = None
    feature_importances: dict[str, float] | None = None
    feature_drift_breakdown: list[FeatureDriftDetail] = []
    reliability_reasons: list[str] = []
    recommendations: list[str] = []
