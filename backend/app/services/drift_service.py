"""
Data Drift Detection Service
Calculates Population Stability Index (PSI) and Kolmogorov-Smirnov statistical tests
to measure distribution drift between baseline and current dataset versions.
Persists overall score to `drift_detection` and detailed breakdown to JSON storage.
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.models.drift_detection import DriftDetection
from app.services.dataset_service import DatasetService

class DriftService:
    @staticmethod
    def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) for a continuous variable.
        PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
        Laplace smoothing (eps=1e-4) is applied to handle zero-count bins safely.
        """
        # Filter out NaN values
        expected_clean = expected[~np.isnan(expected)]
        actual_clean = actual[~np.isnan(actual)]

        if len(expected_clean) == 0 or len(actual_clean) == 0:
            return 0.0

        # Create quantile bins using the baseline (expected) distribution
        quantiles = np.linspace(0, 100, num_bins + 1)
        try:
            bins = np.percentile(expected_clean, quantiles)
            bins = np.unique(bins)
            if len(bins) < 2:
                return 0.0
        except Exception:
            return 0.0

        bins[0] = -np.inf
        bins[-1] = np.inf

        expected_counts, _ = np.histogram(expected_clean, bins=bins)
        actual_counts, _ = np.histogram(actual_clean, bins=bins)

        eps = 1e-4
        expected_pct = (expected_counts + eps) / (len(expected_clean) + eps * len(expected_counts))
        actual_pct = (actual_counts + eps) / (len(actual_clean) + eps * len(actual_counts))

        psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(max(0.0, psi_val))

    @staticmethod
    def calculate_categorical_psi(expected_series: pd.Series, actual_series: pd.Series) -> float:
        """
        Calculates PSI for categorical features across discrete category frequencies.
        """
        exp_counts = expected_series.value_counts(dropna=False)
        act_counts = actual_series.value_counts(dropna=False)

        all_categories = set(exp_counts.index).union(set(act_counts.index))
        if not all_categories:
            return 0.0

        eps = 1e-4
        total_exp = len(expected_series) + eps * len(all_categories)
        total_act = len(actual_series) + eps * len(all_categories)

        psi_val = 0.0
        for cat in all_categories:
            e_pct = (exp_counts.get(cat, 0) + eps) / total_exp
            a_pct = (act_counts.get(cat, 0) + eps) / total_act
            psi_val += (a_pct - e_pct) * np.log(a_pct / e_pct)

        return float(max(0.0, psi_val))

    @staticmethod
    def detect_drift_for_evaluation(
        db: Session,
        evaluation_id: int,
        dataset_version_id: int
    ) -> DriftDetection:
        """
        Finds previous baseline version for the dataset, runs statistical drift tests,
        and saves the consolidated drift metric in `drift_detection`.
        """
        current_version = db.query(DatasetVersion).filter(DatasetVersion.dataset_version_id == dataset_version_id).first()
        if not current_version:
            raise HTTPException(status_code=404, detail="Dataset version not found.")

        # Identify reference version: prior version of the same dataset
        previous_version = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == current_version.dataset_id,
            DatasetVersion.dataset_version_id != current_version.dataset_version_id,
            DatasetVersion.created_date <= current_version.created_date
        ).order_by(DatasetVersion.created_date.desc(), DatasetVersion.dataset_version_id.desc()).first()

        current_file = DatasetService.get_storage_path(current_version.dataset_id, current_version.version_number)
        now = datetime.now()

        # If no baseline exists (Version 1.0 or only 1 version), record baseline zero drift
        if not previous_version or not current_file.exists():
            drift_obj = DriftDetection(
                evaluation_id=evaluation_id,
                drift_score=Decimal("0.0000"),
                drift_status="LOW",
                detected_date=now
            )
            db.add(drift_obj)
            db.commit()
            db.refresh(drift_obj)

            # Write baseline report JSON
            report = {
                "evaluation_id": evaluation_id,
                "current_version": current_version.version_number,
                "reference_version": None,
                "overall_drift_score": 0.0,
                "drift_status": "LOW",
                "explanation": "No prior reference version found for this dataset. This version serves as the initial statistical baseline.",
                "feature_breakdown": []
            }
            DriftService._save_drift_report(evaluation_id, report)
            return drift_obj

        prev_file = DatasetService.get_storage_path(previous_version.dataset_id, previous_version.version_number)
        if not prev_file.exists():
            drift_obj = DriftDetection(
                evaluation_id=evaluation_id,
                drift_score=Decimal("0.0000"),
                drift_status="LOW",
                detected_date=now
            )
            db.add(drift_obj)
            db.commit()
            db.refresh(drift_obj)
            return drift_obj

        # Load datasets
        df_curr = pd.read_csv(current_file)
        df_prev = pd.read_csv(prev_file)

        # Common features to compare
        common_cols = [c for c in df_curr.columns if c in df_prev.columns]
        feature_breakdown = []
        psi_scores = []

        for col in common_cols:
            if pd.api.types.is_numeric_dtype(df_curr[col]) and pd.api.types.is_numeric_dtype(df_prev[col]):
                psi = DriftService.calculate_psi(df_prev[col].values, df_curr[col].values)
                # Two-sample Kolmogorov-Smirnov test
                try:
                    ks_res = stats.ks_2samp(df_prev[col].dropna(), df_curr[col].dropna())
                    p_val = float(round(ks_res.pvalue, 5))
                except Exception:
                    p_val = None

                psi_scores.append(psi)
                level = "HIGH" if psi > 0.25 else ("MEDIUM" if psi >= 0.10 else "LOW")
                feature_breakdown.append({
                    "feature_name": col,
                    "feature_type": "numerical",
                    "psi_score": round(psi, 4),
                    "p_value": p_val,
                    "drift_level": level,
                    "explanation": f"PSI is {psi:.4f} ({level}). Distribution shifted compared to v{previous_version.version_number}."
                })
            else:
                psi = DriftService.calculate_categorical_psi(df_prev[col], df_curr[col])
                psi_scores.append(psi)
                level = "HIGH" if psi > 0.25 else ("MEDIUM" if psi >= 0.10 else "LOW")
                feature_breakdown.append({
                    "feature_name": col,
                    "feature_type": "categorical",
                    "psi_score": round(psi, 4),
                    "p_value": None,
                    "drift_level": level,
                    "explanation": f"Categorical PSI is {psi:.4f} ({level}). Category frequency changed."
                })

        mean_psi = float(np.mean(psi_scores)) if psi_scores else 0.0
        drift_score_rounded = round(mean_psi, 4)

        if drift_score_rounded > 0.25:
            drift_status = "HIGH"
            explanation = f"Significant data drift detected (mean PSI = {drift_score_rounded:.4f}). Key shifted features: " + \
                          ", ".join([f["feature_name"] for f in sorted(feature_breakdown, key=lambda x: x["psi_score"], reverse=True)[:3]])
        elif drift_score_rounded >= 0.10:
            drift_status = "MEDIUM"
            explanation = f"Moderate data drift detected (mean PSI = {drift_score_rounded:.4f}). Continuous monitoring recommended."
        else:
            drift_status = "LOW"
            explanation = f"Low data drift (mean PSI = {drift_score_rounded:.4f}). Current distribution closely matches reference v{previous_version.version_number}."

        drift_obj = DriftDetection(
            evaluation_id=evaluation_id,
            drift_score=Decimal(str(drift_score_rounded)),
            drift_status=drift_status,
            detected_date=now
        )
        db.add(drift_obj)
        db.commit()
        db.refresh(drift_obj)

        report = {
            "evaluation_id": evaluation_id,
            "current_version": current_version.version_number,
            "reference_version": previous_version.version_number,
            "overall_drift_score": drift_score_rounded,
            "drift_status": drift_status,
            "explanation": explanation,
            "feature_breakdown": feature_breakdown
        }
        DriftService._save_drift_report(evaluation_id, report)
        return drift_obj

    @staticmethod
    def _save_drift_report(evaluation_id: int, report_dict: dict):
        report_file = settings.REPORT_STORAGE_PATH / f"drift_eval_{evaluation_id}.json"
        with open(report_file, "w") as f:
            json.dump(report_dict, f, indent=2)

    @staticmethod
    def get_drift_report(evaluation_id: int) -> dict | None:
        report_file = settings.REPORT_STORAGE_PATH / f"drift_eval_{evaluation_id}.json"
        if report_file.exists():
            with open(report_file, "r") as f:
                return json.load(f)
        return None
