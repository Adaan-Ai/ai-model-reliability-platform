"""
Router: Datasets & Dataset Versions API
Manages Dataset metadata, CSV uploads, file profiling, and version tracking (Core Entities 3 & 4).
"""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.database import get_db
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.data_source import DataSource
from app.models.user import User
from app.models.quality_result import DataQualityResult
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetRead, DatasetDetail,
    DatasetVersionRead, DatasetVersionDetail
)
from app.services.dataset_service import DatasetService
from app.services.quality_service import QualityService

router = APIRouter(tags=["Datasets"])

@router.get("/datasets", response_model=list[DatasetRead])
def get_datasets(db: Session = Depends(get_db)):
    """List all registered datasets with version count and latest version tag."""
    datasets = db.query(Dataset).all()
    results = []
    for d in datasets:
        v_count = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == d.dataset_id).count()
        latest_v = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == d.dataset_id
        ).order_by(DatasetVersion.created_date.desc(), DatasetVersion.dataset_version_id.desc()).first()

        item = DatasetRead.model_validate(d)
        item.version_count = v_count
        item.latest_version = latest_v.version_number if latest_v else None
        results.append(item)
    return results

@router.post("/datasets", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def create_dataset_metadata(d_in: DatasetCreate, db: Session = Depends(get_db)):
    """Register dataset metadata without file."""
    # Verify owner & source exist
    if not db.query(User).filter(User.user_id == d_in.owner_id).first():
        raise HTTPException(status_code=400, detail="Owner user does not exist.")
    if not db.query(DataSource).filter(DataSource.source_id == d_in.source_id).first():
        raise HTTPException(status_code=400, detail="Data Source does not exist.")

    ds = Dataset(
        dataset_name=d_in.dataset_name,
        description=d_in.description,
        source_id=d_in.source_id,
        owner_id=d_in.owner_id,
        created_date=d_in.created_date or date.today()
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)

    # Initialize default quality checks
    DatasetService.create_default_quality_checks(db, ds.dataset_id)
    return DatasetRead.model_validate(ds)

@router.post("/datasets/upload", response_model=DatasetDetail, status_code=status.HTTP_201_CREATED)
async def upload_new_dataset(
    file: UploadFile = File(...),
    dataset_name: str = Form(...),
    description: str = Form(""),
    source_id: int = Form(...),
    owner_id: int = Form(...),
    version_number: str = Form("1.0"),
    db: Session = Depends(get_db)
):
    """
    Registers a new dataset, saves CSV safely, profiles columns and missing values,
    creates its first DATASET_VERSION record, and auto-executes baseline data quality checks.
    """
    if not db.query(User).filter(User.user_id == owner_id).first():
        raise HTTPException(status_code=400, detail="Owner user not found.")
    if not db.query(DataSource).filter(DataSource.source_id == source_id).first():
        raise HTTPException(status_code=400, detail="Data Source not found.")

    # 1. Create dataset entity
    dataset = Dataset(
        dataset_name=dataset_name,
        description=description,
        source_id=source_id,
        owner_id=owner_id,
        created_date=date.today()
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # 2. Save CSV to safe storage
    saved_path = DatasetService.validate_and_save_csv(file, dataset.dataset_id, version_number)

    # 3. Profile file with Pandas
    profile = DatasetService.profile_csv(saved_path)

    # 4. Create first DATASET_VERSION
    version = DatasetVersion(
        dataset_id=dataset.dataset_id,
        version_number=version_number,
        record_count=profile["record_count"],
        created_date=date.today()
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    # 5. Initialize & execute default quality checks against this version
    DatasetService.create_default_quality_checks(db, dataset.dataset_id)
    QualityService.run_checks_for_version(db, version.dataset_version_id)

    res = DatasetDetail.model_validate(dataset)
    res.versions = [DatasetVersionRead.model_validate(version)]
    return res

@router.post("/datasets/{dataset_id}/upload-version", response_model=DatasetVersionDetail, status_code=status.HTTP_201_CREATED)
async def upload_new_dataset_version(
    dataset_id: int,
    file: UploadFile = File(...),
    version_number: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a new CSV version for an existing dataset (e.g. v2.0 with drift or updates).
    Never overwrites previous versions.
    """
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # Check unique version number for this dataset
    existing_v = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.version_number == version_number
    ).first()
    if existing_v:
        raise HTTPException(status_code=400, detail=f"Version '{version_number}' already exists for this dataset.")

    # Save CSV
    saved_path = DatasetService.validate_and_save_csv(file, dataset_id, version_number)

    # Profile CSV
    profile = DatasetService.profile_csv(saved_path)

    # Create DATASET_VERSION
    version = DatasetVersion(
        dataset_id=dataset_id,
        version_number=version_number,
        record_count=profile["record_count"],
        created_date=date.today()
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    # Auto-run quality checks on the new version
    QualityService.run_checks_for_version(db, version.dataset_version_id)

    res = DatasetVersionDetail.model_validate(version)
    res.dataset_name = dataset.dataset_name
    res.file_exists = True
    res.columns = profile["columns"]
    res.numerical_columns = profile["numerical_columns"]
    res.categorical_columns = profile["categorical_columns"]
    res.preview = profile["preview"]
    return res

@router.get("/datasets/{dataset_id}", response_model=DatasetDetail)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Retrieve complete dataset details with all associated versions."""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    
    versions = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id
    ).order_by(DatasetVersion.created_date.desc()).all()

    res = DatasetDetail.model_validate(dataset)
    res.versions = [DatasetVersionRead.model_validate(v) for v in versions]
    return res

@router.put("/datasets/{dataset_id}", response_model=DatasetRead)
def update_dataset(dataset_id: int, d_up: DatasetUpdate, db: Session = Depends(get_db)):
    """Update dataset metadata."""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if d_up.dataset_name is not None:
        dataset.dataset_name = d_up.dataset_name
    if d_up.description is not None:
        dataset.description = d_up.description
    if d_up.source_id is not None:
        dataset.source_id = d_up.source_id
    if d_up.owner_id is not None:
        dataset.owner_id = d_up.owner_id

    db.commit()
    db.refresh(dataset)
    return DatasetRead.model_validate(dataset)

@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset, its dependent records, and stored dataset/report files."""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    dataset_files = [
        DatasetService.get_storage_path(dataset.dataset_id, version.version_number)
        for version in dataset.versions
    ]
    evaluation_ids = [
        evaluation.evaluation_id
        for version in dataset.versions
        for evaluation in version.evaluations
    ]
    report_files = [
        report_path
        for evaluation_id in evaluation_ids
        for report_path in (
            settings.REPORT_STORAGE_PATH / f"evaluation_{evaluation_id}_report.json",
            settings.REPORT_STORAGE_PATH / f"drift_eval_{evaluation_id}.json",
        )
    ]

    db.delete(dataset)
    db.commit()

    cleanup_failures = []
    for file_path in dataset_files + report_files:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            cleanup_failures.append(file_path.name)
    if cleanup_failures:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dataset was deleted, but stored files could not be removed: {', '.join(cleanup_failures)}"
        )
    return None

@router.get("/datasets/{dataset_id}/versions", response_model=list[DatasetVersionRead])
def get_dataset_versions(dataset_id: int, db: Session = Depends(get_db)):
    """List all version records for a dataset."""
    return db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id
    ).order_by(DatasetVersion.created_date.desc()).all()

@router.get("/dataset-versions/{version_id}", response_model=DatasetVersionDetail)
def get_dataset_version_detail(version_id: int, db: Session = Depends(get_db)):
    """Inspect a specific dataset version with column types, preview data, and quality status."""
    v = db.query(DatasetVersion).filter(DatasetVersion.dataset_version_id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Dataset version not found.")

    dataset = db.query(Dataset).filter(Dataset.dataset_id == v.dataset_id).first()
    file_path = DatasetService.get_storage_path(v.dataset_id, v.version_number)

    res = DatasetVersionDetail.model_validate(v)
    res.dataset_name = dataset.dataset_name if dataset else None

    if file_path.exists():
        res.file_exists = True
        profile = DatasetService.profile_csv(file_path)
        res.columns = profile["columns"]
        res.numerical_columns = profile["numerical_columns"]
        res.categorical_columns = profile["categorical_columns"]
        res.preview = profile["preview"]
    else:
        res.file_exists = False

    # Quality Summary
    dq_results = db.query(DataQualityResult).filter(DataQualityResult.dataset_version_id == version_id).all()
    if dq_results:
        avg_score = float(sum(r.score for r in dq_results) / len(dq_results))
        res.quality_summary = {
            "total_checks": len(dq_results),
            "average_score": round(avg_score, 2),
            "passed": sum(1 for r in dq_results if r.status == "PASSED"),
            "warning": sum(1 for r in dq_results if r.status == "WARNING"),
            "failed": sum(1 for r in dq_results if r.status == "FAILED"),
        }

    return res
