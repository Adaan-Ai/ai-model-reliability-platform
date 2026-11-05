"""
Router: Reliability Scoring API
Endpoints for inspecting holistic reliability indices and explainability breakdowns (Core Entity 12).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reliability_score import ReliabilityScore
from app.schemas.reliability import ReliabilityScoreRead, ReliabilityReportDetail
from app.services.reliability_service import ReliabilityService

router = APIRouter(tags=["Reliability"])

@router.get("/reliability", response_model=list[ReliabilityScoreRead])
def get_all_reliability_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all calculated reliability scores with parent model and dataset metadata."""
    records = db.query(ReliabilityScore).offset(skip).limit(limit).all()
    results = []
    for r in records:
        run = r.evaluation
        mv = run.model_version if run else None
        dv = run.dataset_version if run else None
        m = mv.model if mv else None
        dataset = dv.dataset if dv else None

        item = ReliabilityScoreRead.model_validate(r)
        item.model_name = m.model_name if m else None
        item.model_version = mv.version_number if mv else None
        item.dataset_name = dataset.dataset_name if dataset else None
        item.dataset_version = dv.version_number if dv else None
        results.append(item)
    return results

@router.get("/evaluations/{evaluation_id}/reliability", response_model=ReliabilityReportDetail)
def get_evaluation_reliability_detail(evaluation_id: int, db: Session = Depends(get_db)):
    """Inspect complete reliability calculation, formula weights, diagnostic reasons, and recommendations."""
    r = db.query(ReliabilityScore).filter(ReliabilityScore.evaluation_id == evaluation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reliability score not found for this evaluation.")

    run = r.evaluation
    mv = run.model_version if run else None
    dv = run.dataset_version if run else None
    m = mv.model if mv else None
    dataset = dv.dataset if dv else None

    item = ReliabilityReportDetail.model_validate(r)
    item.model_name = m.model_name if m else None
    item.model_version = mv.version_number if mv else None
    item.dataset_name = dataset.dataset_name if dataset else None
    item.dataset_version = dv.version_number if dv else None

    item.formula_explanation = (
        "Overall Reliability = (0.35 × Data Quality Score) + "
        "(0.45 × Model Performance Score) + (0.20 × Drift Health Score)"
    )
    item.component_weights = {
        "data_quality": ReliabilityService.WEIGHT_DATA_QUALITY,
        "model_performance": ReliabilityService.WEIGHT_MODEL_PERF,
        "drift_health": ReliabilityService.WEIGHT_DRIFT_HEALTH,
    }

    reasons, recs = ReliabilityService.generate_diagnostic_reasons_and_recommendations(
        data_quality_score=float(r.data_quality_score),
        model_perf_score=float(r.model_performance_score),
        drift_health_score=float(r.drift_score),
        overall_score=float(r.overall_score),
        rating=r.rating
    )
    item.reasons = reasons
    item.recommendations = recs

    return item

@router.get("/reliability/formula")
def get_formula_documentation():
    """Retrieve transparent documentation of the platform reliability formula and rating thresholds."""
    return {
        "formula": "Overall Reliability = (0.35 × Data Quality) + (0.45 × Model Performance) + (0.20 × Drift Health)",
        "weights": {
            "data_quality": 0.35,
            "model_performance": 0.45,
            "drift_health": 0.20,
        },
        "normalization": "All component scores normalized between 0.00 and 100.00.",
        "model_performance_formula": "Model Performance = 0.40 × Accuracy + 0.60 × F1-Score (weighted harmonic mean)",
        "drift_health_formula": "Drift Health = max(0, 100 - (PSI_drift_score × 200))",
        "rating_thresholds": {
            "HIGH": "80.00 – 100.00 (Production Approved)",
            "MEDIUM": "60.00 – 79.99 (Conditional Approval / Active Monitoring)",
            "LOW": "Below 60.00 (Critical Attention Required / Deployment Halted)",
        }
    }
