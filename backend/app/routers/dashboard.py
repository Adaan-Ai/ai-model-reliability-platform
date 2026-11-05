"""
Router: Dashboard Analytics API
Calculates real-time aggregations, metrics, distributions, and historical trends
directly from the MySQL database (Module 1).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.ai_model import AIModel
from app.models.model_version import ModelVersion
from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.models.quality_result import DataQualityResult
from app.models.drift_detection import DriftDetection
from app.models.reliability_score import ReliabilityScore
from app.schemas.dashboard import DashboardOverview, TrendPoint, ReliabilityDistribution
from app.routers.evaluations import _hydrate_run_read

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Computes consolidated dashboard statistics directly from MySQL database tables.
    Returns zero counts and empty trend lists when empty (no hardcoded metrics).
    """
    total_datasets = db.query(Dataset).count()
    total_dataset_versions = db.query(DatasetVersion).count()
    total_models = db.query(AIModel).count()
    total_model_versions = db.query(ModelVersion).count()
    total_evaluations = db.query(EvaluationRun).count()

    # Average Model Accuracy
    avg_acc_val = db.query(func.avg(EvaluationResult.accuracy)).scalar()
    avg_model_accuracy = round(float(avg_acc_val), 2) if avg_acc_val is not None else 0.0

    # Average Data Quality Score
    avg_dq_val = db.query(func.avg(DataQualityResult.score)).scalar()
    avg_data_quality_score = round(float(avg_dq_val), 2) if avg_dq_val is not None else 0.0

    # High-drift detections
    high_drift_count = db.query(DriftDetection).filter(DriftDetection.drift_status == "HIGH").count()

    # Low-reliability evaluations
    low_reliability_count = db.query(ReliabilityScore).filter(ReliabilityScore.rating == "LOW").count()

    # Performance trends (ordered chronological evaluation runs)
    perf_runs = db.query(EvaluationRun).filter(EvaluationRun.status == "COMPLETED").order_by(
        EvaluationRun.execution_date.asc()
    ).limit(15).all()

    performance_trends = []
    drift_trends = []
    for r in perf_runs:
        label = f"{r.model_version.model.model_name if r.model_version and r.model_version.model else 'Model'} v{r.model_version.version_number if r.model_version else ''}"
        date_str = r.execution_date.strftime("%b %d %H:%M")
        
        acc = float(r.result.accuracy) if r.result else 0.0
        f1 = float(r.result.f1_score) if r.result else 0.0
        performance_trends.append(TrendPoint(date=date_str, label=label, value=acc, secondary_value=f1))

        # Drift trend
        drift_item = db.query(DriftDetection).filter(DriftDetection.evaluation_id == r.evaluation_id).first()
        if drift_item:
            drift_trends.append(TrendPoint(
                date=date_str,
                label=label,
                value=float(drift_item.drift_score)
            ))

    # Data Quality trends (recent dataset versions and their average check score)
    versions = db.query(DatasetVersion).order_by(DatasetVersion.created_date.asc()).limit(10).all()
    quality_trends = []
    for v in versions:
        avg_score = db.query(func.avg(DataQualityResult.score)).filter(
            DataQualityResult.dataset_version_id == v.dataset_version_id
        ).scalar()
        if avg_score is not None:
            quality_trends.append(TrendPoint(
                date=v.created_date.strftime("%Y-%m-%d"),
                label=f"{v.dataset.dataset_name if v.dataset else 'Data'} v{v.version_number}",
                value=round(float(avg_score), 2)
            ))

    # Reliability distribution
    rel_counts = {
        "HIGH": db.query(ReliabilityScore).filter(ReliabilityScore.rating == "HIGH").count(),
        "MEDIUM": db.query(ReliabilityScore).filter(ReliabilityScore.rating == "MEDIUM").count(),
        "LOW": db.query(ReliabilityScore).filter(ReliabilityScore.rating == "LOW").count(),
    }
    total_rel = sum(rel_counts.values())
    reliability_dist = [
        ReliabilityDistribution(
            rating=k,
            count=v,
            percentage=round((v / max(1, total_rel)) * 100.0, 1) if total_rel > 0 else 0.0
        )
        for k, v in rel_counts.items()
    ]

    # Recent evaluation history
    recent_runs = db.query(EvaluationRun).order_by(
        EvaluationRun.execution_date.desc()
    ).limit(8).all()
    hydrated_recents = [_hydrate_run_read(r, db) for r in recent_runs]

    return DashboardOverview(
        total_datasets=total_datasets,
        total_dataset_versions=total_dataset_versions,
        total_models=total_models,
        total_model_versions=total_model_versions,
        total_evaluations=total_evaluations,
        avg_model_accuracy=avg_model_accuracy,
        avg_data_quality_score=avg_data_quality_score,
        high_drift_count=high_drift_count,
        low_reliability_count=low_reliability_count,
        performance_trends=performance_trends,
        quality_trends=quality_trends,
        drift_trends=drift_trends,
        reliability_distribution=reliability_dist,
        recent_evaluations=hydrated_recents
    )
