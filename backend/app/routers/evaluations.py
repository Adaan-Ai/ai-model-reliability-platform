"""
Router: Model Evaluation Engine API
Endpoints for launching Scikit-learn evaluations, viewing lineage, and comparing runs (Core Entities 9 & 10).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.models.model_version import ModelVersion
from app.models.ai_model import AIModel
from app.models.dataset_version import DatasetVersion
from app.models.dataset import Dataset
from app.models.drift_detection import DriftDetection
from app.models.reliability_score import ReliabilityScore
from app.schemas.evaluation import (
    EvaluationRunCreate, EvaluationRunRead, EvaluationRunDetail, EvaluationResultRead
)
from app.schemas.drift import DriftDetectionRead, FeatureDriftDetail
from app.schemas.reliability import ReliabilityScoreRead
from app.schemas.user import UserRead
from app.services.evaluation_service import EvaluationService
from app.services.drift_service import DriftService

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

def _hydrate_run_read(r: EvaluationRun, db: Session) -> EvaluationRunRead:
    mv = r.model_version
    dv = r.dataset_version
    m = mv.model if mv else None
    d = dv.dataset if dv else None

    # Construct EvaluationRunRead explicitly to avoid relationship collisions
    item = EvaluationRunRead(
        evaluation_id=r.evaluation_id,
        model_version_id=r.model_version_id,
        dataset_version_id=r.dataset_version_id,
        executed_by=r.executed_by,
        execution_date=r.execution_date,
        status=r.status,
        model_name=m.model_name if m else None,
        model_version_number=mv.version_number if mv else None,
        algorithm=mv.algorithm if mv else None,
        dataset_name=d.dataset_name if d else None,
        dataset_version_number=dv.version_number if dv else None,
        executor=UserRead.model_validate(r.executor) if r.executor else None,
        result=EvaluationResultRead.model_validate(r.result) if r.result else None
    )
    
    # Drift
    drift = db.query(DriftDetection).filter(DriftDetection.evaluation_id == r.evaluation_id).first()
    if drift:
        dr = DriftDetectionRead.model_validate(drift)
        dr.model_name = item.model_name
        dr.model_version = item.model_version_number
        dr.dataset_name = item.dataset_name
        dr.dataset_version = item.dataset_version_number
        item.drift = dr

    # Reliability
    rel = db.query(ReliabilityScore).filter(ReliabilityScore.evaluation_id == r.evaluation_id).first()
    if rel:
        rs = ReliabilityScoreRead.model_validate(rel)
        rs.model_name = item.model_name
        rs.model_version = item.model_version_number
        rs.dataset_name = item.dataset_name
        rs.dataset_version = item.dataset_version_number
        item.reliability = rs

    return item

@router.get("", response_model=list[EvaluationRunRead])
def get_evaluations(
    model_id: int | None = None,
    dataset_id: int | None = None,
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List evaluation runs with optional filtering by model, dataset, or status."""
    query = db.query(EvaluationRun)
    if status_filter:
        query = query.filter(EvaluationRun.status == status_filter.upper())
    if model_id:
        query = query.join(ModelVersion).filter(ModelVersion.model_id == model_id)
    if dataset_id:
        query = query.join(DatasetVersion).filter(DatasetVersion.dataset_id == dataset_id)

    runs = query.order_by(EvaluationRun.execution_date.desc()).offset(skip).limit(limit).all()
    return [_hydrate_run_read(r, db) for r in runs]

@router.post("", response_model=EvaluationRunRead, status_code=status.HTTP_201_CREATED)
def trigger_evaluation(req: EvaluationRunCreate, db: Session = Depends(get_db)):
    """
    Executes an end-to-end evaluation run:
    1. Trains/evaluates model using Scikit-learn
    2. Calculates performance metrics (Accuracy, Precision, Recall, F1)
    3. Runs Drift Detection against reference version
    4. Computes Overall Reliability Score
    5. Saves full JSON audit report
    """
    run = EvaluationService.run_evaluation(db, req)
    return _hydrate_run_read(run, db)

@router.get("/compare", response_model=list[EvaluationRunRead])
def compare_evaluations(
    ids: list[int] = Query(..., description="List of evaluation IDs to compare side by side"),
    db: Session = Depends(get_db)
):
    """Compare performance, drift, and reliability metrics across multiple evaluation runs."""
    runs = db.query(EvaluationRun).filter(EvaluationRun.evaluation_id.in_(ids)).all()
    return [_hydrate_run_read(r, db) for r in runs]

@router.get("/{evaluation_id}", response_model=EvaluationRunDetail)
def get_evaluation_detail(evaluation_id: int, db: Session = Depends(get_db)):
    """Retrieve full evaluation report including confusion matrix, classification report, and drift breakdown."""
    run = db.query(EvaluationRun).filter(EvaluationRun.evaluation_id == evaluation_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found.")

    base_read = _hydrate_run_read(run, db)
    detail_data = base_read.model_dump()

    # Load stored comprehensive report JSON
    rep_dict = EvaluationService.get_evaluation_report(evaluation_id)
    if rep_dict:
        detail_data["confusion_matrix"] = rep_dict.get("confusion_matrix")
        detail_data["class_labels"] = rep_dict.get("class_labels")
        detail_data["classification_report"] = rep_dict.get("classification_report")
        detail_data["reliability_reasons"] = rep_dict.get("reasons", [])
        detail_data["recommendations"] = rep_dict.get("recommendations", [])

    # Load stored drift breakdown JSON
    drift_dict = DriftService.get_drift_report(evaluation_id)
    if drift_dict:
        detail_data["feature_drift_breakdown"] = [
            FeatureDriftDetail.model_validate(fb) for fb in drift_dict.get("feature_breakdown", [])
        ]

    return EvaluationRunDetail(**detail_data)

@router.get("/{evaluation_id}/results", response_model=EvaluationResultRead)
def get_evaluation_result(evaluation_id: int, db: Session = Depends(get_db)):
    """Retrieve raw performance metrics for an evaluation run."""
    res = db.query(EvaluationResult).filter(EvaluationResult.evaluation_id == evaluation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Evaluation result not found.")
    return res
