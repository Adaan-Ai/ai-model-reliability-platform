"""
Pydantic Schemas: DriftDetection
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class DriftDetectionBase(BaseModel):
    evaluation_id: int
    drift_score: Decimal | float = Field(ge=0.0)
    drift_status: str  # LOW, MEDIUM, HIGH
    detected_date: datetime

class DriftDetectionRead(DriftDetectionBase):
    drift_id: int
    model_name: str | None = None
    model_version: str | None = None
    dataset_name: str | None = None
    dataset_version: str | None = None
    reference_version: str | None = None
    model_config = ConfigDict(from_attributes=True)

class FeatureDriftDetail(BaseModel):
    feature_name: str
    feature_type: str  # numerical or categorical
    psi_score: float
    p_value: float | None = None  # From KS-test
    drift_level: str  # LOW, MEDIUM, HIGH
    explanation: str

class DriftReportDetail(DriftDetectionRead):
    feature_drift_breakdown: list[FeatureDriftDetail] = []
    overall_explanation: str | None = None
