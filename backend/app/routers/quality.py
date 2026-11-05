"""
Router: Data Quality Monitoring API
Endpoints for defining checks, triggering executions against real data, and viewing results (Core Entities 5 & 6).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quality_check import DataQualityCheck
from app.models.quality_result import DataQualityResult
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.schemas.quality import (
    QualityCheckCreate, QualityCheckRead,
    QualityResultRead, RunQualityChecksRequest
)
from app.services.quality_service import QualityService

router = APIRouter(tags=["Data Quality"])

@router.post("/quality-checks", response_model=QualityCheckRead, status_code=status.HTTP_201_CREATED)
def create_quality_check(chk_in: QualityCheckCreate, db: Session = Depends(get_db)):
    """Define a new custom data quality check for a dataset."""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == chk_in.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    chk = DataQualityCheck(
        dataset_id=chk_in.dataset_id,
        check_name=chk_in.check_name,
        check_type=chk_in.check_type,
        threshold=chk_in.threshold
    )
    db.add(chk)
    db.commit()
    db.refresh(chk)
    return chk

@router.get("/quality-checks", response_model=list[QualityCheckRead])
def get_quality_checks(dataset_id: int | None = None, db: Session = Depends(get_db)):
    """List data quality check definitions, optionally filtered by dataset."""
    query = db.query(DataQualityCheck)
    if dataset_id is not None:
        query = query.filter(DataQualityCheck.dataset_id == dataset_id)
    return query.all()

@router.post("/dataset-versions/{version_id}/run-quality-checks", response_model=list[QualityResultRead])
def run_quality_checks_for_version(
    version_id: int,
    req: RunQualityChecksRequest = RunQualityChecksRequest(),
    db: Session = Depends(get_db)
):
    """
    Executes actual quality checks against the dataset version CSV.
    Computes scores and assigns deterministic status (PASSED, WARNING, FAILED).
    """
    results = QualityService.run_checks_for_version(db, version_id, req.check_ids)
    
    # Enrich response with check metadata
    out = []
    for r in results:
        item = QualityResultRead.model_validate(r)
        if r.quality_check:
            item.check_name = r.quality_check.check_name
            item.check_type = r.quality_check.check_type
            item.threshold = r.quality_check.threshold
        out.append(item)
    return out

@router.get("/dataset-versions/{version_id}/quality-results", response_model=list[QualityResultRead])
def get_quality_results_for_version(version_id: int, db: Session = Depends(get_db)):
    """Retrieve all quality results evaluated on a specific dataset version."""
    results = db.query(DataQualityResult).filter(
        DataQualityResult.dataset_version_id == version_id
    ).order_by(DataQualityResult.execution_date.desc()).all()

    out = []
    for r in results:
        item = QualityResultRead.model_validate(r)
        if r.quality_check:
            item.check_name = r.quality_check.check_name
            item.check_type = r.quality_check.check_type
            item.threshold = r.quality_check.threshold
        out.append(item)
    return out

@router.get("/quality-results", response_model=list[QualityResultRead])
def get_all_quality_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List recent quality results across all datasets."""
    results = db.query(DataQualityResult).order_by(
        DataQualityResult.execution_date.desc()
    ).offset(skip).limit(limit).all()

    out = []
    for r in results:
        item = QualityResultRead.model_validate(r)
        if r.quality_check:
            item.check_name = r.quality_check.check_name
            item.check_type = r.quality_check.check_type
            item.threshold = r.quality_check.threshold
        out.append(item)
    return out
