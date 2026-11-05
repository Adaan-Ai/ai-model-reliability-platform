"""
Pydantic Schemas: Dashboard
Aggregation and trend schemas for enterprise analytics overview
"""

from pydantic import BaseModel
from app.schemas.evaluation import EvaluationRunRead

class TrendPoint(BaseModel):
    date: str
    label: str
    value: float
    secondary_value: float | None = None

class ReliabilityDistribution(BaseModel):
    rating: str  # HIGH, MEDIUM, LOW
    count: int
    percentage: float

class DashboardOverview(BaseModel):
    total_datasets: int
    total_dataset_versions: int
    total_models: int
    total_model_versions: int
    total_evaluations: int
    avg_model_accuracy: float
    avg_data_quality_score: float
    high_drift_count: int
    low_reliability_count: int

    performance_trends: list[TrendPoint] = []
    quality_trends: list[TrendPoint] = []
    drift_trends: list[TrendPoint] = []
    reliability_distribution: list[ReliabilityDistribution] = []
    recent_evaluations: list[EvaluationRunRead] = []
