"""
Dataset Service
Handles CSV upload, validation, secure storage, Pandas profiling,
and dataset version management.
"""

import re
from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.config import settings
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.quality_check import DataQualityCheck

# Allowed CSV mime types and extensions
ALLOWED_EXTENSIONS = {".csv"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit

class DatasetService:
    @staticmethod
    def get_storage_path(dataset_id: int, version_number: str) -> Path:
        """
        Generates safe, sanitized storage path preventing directory traversal.
        """
        clean_version = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', str(version_number))
        filename = f"dataset_{dataset_id}_v{clean_version}.csv"
        target_path = settings.DATASET_STORAGE_PATH / filename
        # Ensure target_path stays strictly inside DATASET_STORAGE_PATH
        if not target_path.resolve().is_relative_to(settings.DATASET_STORAGE_PATH.resolve()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path detected"
            )
        return target_path

    @staticmethod
    def validate_and_save_csv(file: UploadFile, dataset_id: int, version_number: str) -> Path:
        """
        Validates uploaded file extension and saves safely to disk.
        """
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '{ext}'. Only .csv files are supported."
            )

        storage_path = DatasetService.get_storage_path(dataset_id, version_number)
        
        # Read file contents and verify size
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # Write to target path
        with open(storage_path, "wb") as f:
            f.write(content)

        return storage_path

    @staticmethod
    def profile_csv(file_path: Path) -> dict:
        """
        Reads CSV using Pandas and computes comprehensive metadata profile.
        """
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset file not found on disk."
            )

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse CSV file: {str(e)}"
            )

        row_count = int(len(df))
        col_count = int(len(df.columns))
        columns = list(df.columns)

        # Identify numerical and categorical columns
        numerical_cols = list(df.select_dtypes(include=[np.number]).columns)
        categorical_cols = [c for c in columns if c not in numerical_cols]

        # Missing values
        missing_counts = df.isnull().sum().to_dict()
        total_missing = int(df.isnull().sum().sum())
        total_cells = max(1, row_count * col_count)
        missing_percentage = round((total_missing / total_cells) * 100, 2)

        # Duplicate records
        duplicate_count = int(df.duplicated().sum())
        duplicate_percentage = round((duplicate_count / max(1, row_count)) * 100, 2)

        # Clean preview for JSON response (replace NaN with None)
        preview_df = df.head(10).replace({np.nan: None})
        preview = preview_df.to_dict(orient="records")

        # Basic numerical statistics
        summary_stats = {}
        if numerical_cols:
            desc = df[numerical_cols].describe().replace({np.nan: None}).to_dict()
            summary_stats = desc

        return {
            "record_count": row_count,
            "column_count": col_count,
            "columns": columns,
            "numerical_columns": numerical_cols,
            "categorical_columns": categorical_cols,
            "missing_counts": missing_counts,
            "total_missing": total_missing,
            "missing_percentage": missing_percentage,
            "duplicate_count": duplicate_count,
            "duplicate_percentage": duplicate_percentage,
            "preview": preview,
            "summary_stats": summary_stats,
        }

    @staticmethod
    def create_default_quality_checks(db: Session, dataset_id: int):
        """
        Creates standard baseline quality check definitions for a dataset if none exist.
        """
        existing = db.query(DataQualityCheck).filter(DataQualityCheck.dataset_id == dataset_id).count()
        if existing > 0:
            return

        default_checks = [
            ("Missing Values Integrity", "missing_values", 95.0),
            ("Record Uniqueness (Duplicates)", "duplicates", 95.0),
            ("Data Type Consistency", "data_types", 98.0),
            ("Numerical Range Validity", "numerical_range", 90.0),
            ("Categorical Consistency", "categorical_validity", 90.0),
            ("Schema Integrity", "schema_integrity", 100.0),
        ]

        for name, check_type, threshold in default_checks:
            qc = DataQualityCheck(
                dataset_id=dataset_id,
                check_name=name,
                check_type=check_type,
                threshold=threshold
            )
            db.add(qc)
        db.commit()
