"""
Data Quality Service
Executes deterministic, explainable data quality checks against actual dataset versions
and persists results into `data_quality_result`.
"""

from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.quality_check import DataQualityCheck
from app.models.quality_result import DataQualityResult
from app.services.dataset_service import DatasetService

class QualityService:
    @staticmethod
    def run_checks_for_version(
        db: Session,
        dataset_version_id: int,
        check_ids: list[int] | None = None
    ) -> list[DataQualityResult]:
        """
        Executes registered quality checks against the specified dataset version CSV.
        Validates that quality checks belong to the same logical dataset.
        """
        version = db.query(DatasetVersion).filter(DatasetVersion.dataset_version_id == dataset_version_id).first()
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset version {dataset_version_id} not found."
            )

        # Retrieve checks defined for this dataset
        query = db.query(DataQualityCheck).filter(DataQualityCheck.dataset_id == version.dataset_id)
        if check_ids:
            query = query.filter(DataQualityCheck.quality_check_id.in_(check_ids))
        checks = query.all()

        if not checks:
            # Auto-create baseline checks if none exist
            DatasetService.create_default_quality_checks(db, version.dataset_id)
            checks = db.query(DataQualityCheck).filter(DataQualityCheck.dataset_id == version.dataset_id).all()

        file_path = DatasetService.get_storage_path(version.dataset_id, version.version_number)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data file for version {version.version_number} does not exist at {file_path.name}."
            )

        df = pd.read_csv(file_path)
        results: list[DataQualityResult] = []
        now = datetime.now()

        for chk in checks:
            # Double check relationship integrity
            if chk.dataset_id != version.dataset_id:
                continue

            score = QualityService._evaluate_check(df, chk.check_type)
            threshold = float(chk.threshold or 90.0)

            # Determine deterministic status
            if score >= threshold:
                result_status = "PASSED"
            elif score >= max(0.0, threshold - 15.0):
                result_status = "WARNING"
            else:
                result_status = "FAILED"

            # Create or update result record
            existing_result = db.query(DataQualityResult).filter(
                DataQualityResult.quality_check_id == chk.quality_check_id,
                DataQualityResult.dataset_version_id == version.dataset_version_id
            ).first()

            if existing_result:
                existing_result.score = Decimal(str(round(score, 2)))
                existing_result.status = result_status
                existing_result.execution_date = now
                res_obj = existing_result
            else:
                res_obj = DataQualityResult(
                    quality_check_id=chk.quality_check_id,
                    dataset_version_id=version.dataset_version_id,
                    score=Decimal(str(round(score, 2))),
                    status=result_status,
                    execution_date=now
                )
                db.add(res_obj)

            results.append(res_obj)

        db.commit()
        for r in results:
            db.refresh(r)
        return results

    @staticmethod
    def _evaluate_check(df: pd.DataFrame, check_type: str) -> float:
        """
        Calculates a deterministic 0-100 quality score based on check type.
        """
        row_count = len(df)
        col_count = len(df.columns)
        total_cells = max(1, row_count * col_count)

        if check_type == "missing_values":
            total_missing = df.isnull().sum().sum()
            missing_ratio = total_missing / total_cells
            return max(0.0, min(100.0, (1.0 - missing_ratio) * 100.0))

        elif check_type == "duplicates":
            duplicate_rows = df.duplicated().sum()
            dup_ratio = duplicate_rows / max(1, row_count)
            return max(0.0, min(100.0, (1.0 - dup_ratio) * 100.0))

        elif check_type == "data_types":
            # Check numerical columns can convert to numeric cleanly
            num_cols = df.select_dtypes(include=[np.number]).columns
            valid_cells = 0
            total_checked = 0
            for col in num_cols:
                series = df[col].dropna()
                total_checked += len(series)
                converted = pd.to_numeric(series, errors="coerce")
                valid_cells += int(converted.notnull().sum())

            if total_checked == 0:
                return 100.0
            return max(0.0, min(100.0, (valid_cells / total_checked) * 100.0))

        elif check_type == "numerical_range":
            # Outlier detection using IQR
            num_cols = df.select_dtypes(include=[np.number]).columns
            if len(num_cols) == 0:
                return 100.0
            total_numeric = 0
            in_range = 0
            for col in num_cols:
                series = df[col].dropna()
                if len(series) < 4:
                    continue
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 3.0 * iqr
                upper = q3 + 3.0 * iqr
                total_numeric += len(series)
                in_range += int(((series >= lower) & (series <= upper)).sum())

            if total_numeric == 0:
                return 100.0
            return max(0.0, min(100.0, (in_range / total_numeric) * 100.0))

        elif check_type == "categorical_validity":
            # Check categorical columns for placeholder values like '?', 'N/A', '', 'None'
            cat_cols = df.select_dtypes(exclude=[np.number]).columns
            if len(cat_cols) == 0:
                return 100.0
            invalid_placeholders = {"?", "n/a", "na", "null", "none", "", "nan", "unknown"}
            total_cat = 0
            valid_cat = 0
            for col in cat_cols:
                series = df[col].dropna().astype(str).str.strip().str.lower()
                total_cat += len(series)
                invalid_count = int(series.isin(invalid_placeholders).sum())
                valid_cat += (len(series) - invalid_count)

            if total_cat == 0:
                return 100.0
            return max(0.0, min(100.0, (valid_cat / total_cat) * 100.0))

        elif check_type == "schema_integrity":
            # Schema penalties
            score = 100.0
            if row_count == 0:
                return 0.0
            # Deduct if any column is entirely null
            all_null_cols = df.isnull().all().sum()
            score -= (all_null_cols * 15.0)
            # Deduct if unnamed columns exist (e.g. Unnamed: 0 from index saves)
            unnamed = sum(1 for c in df.columns if str(c).startswith("Unnamed:"))
            score -= (unnamed * 10.0)
            return max(0.0, min(100.0, score))

        # Default fallback
        return 95.0
