"""
Router: Data Drift Monitoring API
Endpoints for inspecting feature-level distribution shifts and drift alerts (Core Entity 11).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.drift_detection import DriftDetection
from app.models.evaluation_run import EvaluationRun
from app.schemas.drift import DriftDetectionRead, DriftReportDetail, FeatureDriftDetail
from app.services.drift_service import DriftService

router = APIRouter(tags=["Drift Monitoring"])

@router.get("/drift", response_model=list[DriftDetectionRead])
def get_all_drift_detections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List recent data drift detections across evaluations."""
    records = db.query(DriftDetection).order_by(DriftDetection.detected_date.desc()).offset(skip).limit(limit).all()
    results = []
    for d in records:
        run = d.evaluation
        mv = run.model_version if run else None
        dv = run.dataset_version if run else None
        m = mv.model if mv else None
        dataset = dv.dataset if dv else None

        item = DriftDetectionRead.model_validate(d)
        item.model_name = m.model_name if m else None
        item.model_version = mv.version_number if mv else None
        item.dataset_name = dataset.dataset_name if dataset else None
        item.dataset_version = dv.version_number if dv else None
        results.append(item)
    return results

@router.get("/evaluations/{evaluation_id}/drift", response_model=DriftReportDetail)
def get_evaluation_drift_detail(evaluation_id: int, db: Session = Depends(get_db)):
    """Inspect full statistical drift breakdown and feature-level PSI for an evaluation."""
    d = db.query(DriftDetection).filter(DriftDetection.evaluation_id == evaluation_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Drift record not found for this evaluation.")

    run = d.evaluation
    mv = run.model_version if run else None
    dv = run.dataset_version if run else None
    m = mv.model if mv else None
    dataset = dv.dataset if dv else None

    item = DriftReportDetail.model_validate(d)
    item.model_name = m.model_name if m else None
    item.model_version = mv.version_number if mv else None
    item.dataset_name = dataset.dataset_name if dataset else None
    item.dataset_version = dv.version_number if dv else None

    # Load stored feature breakdown JSON
    rep = DriftService.get_drift_report(evaluation_id)
    if rep:
        item.reference_version = rep.get("reference_version")
        item.overall_explanation = rep.get("explanation")
        item.feature_drift_breakdown = [
            FeatureDriftDetail.model_validate(fb) for fb in rep.get("feature_breakdown", [])
        ]

    return item
