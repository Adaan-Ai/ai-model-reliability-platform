"""
Pydantic Schemas: ReliabilityScore
"""

from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class ReliabilityScoreBase(BaseModel):
    evaluation_id: int
    data_quality_score: Decimal | float = Field(ge=0.0, le=100.0)
    model_performance_score: Decimal | float = Field(ge=0.0, le=100.0)
    drift_score: Decimal | float = Field(ge=0.0, le=100.0)
    overall_score: Decimal | float = Field(ge=0.0, le=100.0)
    rating: str  # LOW, MEDIUM, HIGH

class ReliabilityScoreRead(ReliabilityScoreBase):
    reliability_id: int
    model_name: str | None = None
    model_version: str | None = None
    dataset_name: str | None = None
    dataset_version: str | None = None
    model_config = ConfigDict(from_attributes=True)

class ReliabilityReportDetail(ReliabilityScoreRead):
    formula_explanation: str
    component_weights: dict[str, float]
    reasons: list[str]
    recommendations: list[str]
