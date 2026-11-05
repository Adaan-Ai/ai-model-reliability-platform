"""
Reliability Scoring Engine
Computes the signature composite reliability score for an evaluation run:
Overall Reliability = (0.35 * Data Quality Score) + (0.45 * Model Performance Score) + (0.20 * Drift Health Score)
Generates explainable diagnostic reasons and actionable recommendations.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.models.drift_detection import DriftDetection
from app.models.reliability_score import ReliabilityScore
from app.models.quality_result import DataQualityResult

class ReliabilityService:
    WEIGHT_DATA_QUALITY = 0.35
    WEIGHT_MODEL_PERF = 0.45
    WEIGHT_DRIFT_HEALTH = 0.20

    @staticmethod
    def calculate_reliability(
        db: Session,
        evaluation_id: int
    ) -> ReliabilityScore:
        """
        Consolidates Data Quality, Model Performance, and Drift Health into a single
        composite reliability score and rating.
        """
        run = db.query(EvaluationRun).filter(EvaluationRun.evaluation_id == evaluation_id).first()
        if not run:
            raise ValueError(f"EvaluationRun {evaluation_id} not found.")

        # 1. Data Quality Score (0 - 100)
        # Average of quality check results for this dataset version
        dq_avg = db.query(func.avg(DataQualityResult.score)).filter(
            DataQualityResult.dataset_version_id == run.dataset_version_id
        ).scalar()
        data_quality_score = float(dq_avg) if dq_avg is not None else 100.0

        # 2. Model Performance Score (0 - 100)
        # Balanced formula: 40% Accuracy + 60% F1-score (harmonic mean penalizes false positives and false negatives)
        eval_result = db.query(EvaluationResult).filter(EvaluationResult.evaluation_id == evaluation_id).first()
        if eval_result:
            acc = float(eval_result.accuracy)
            f1 = float(eval_result.f1_score)
            model_perf_score = (0.40 * acc) + (0.60 * f1)
        else:
            model_perf_score = 0.0

        # 3. Drift Health Score (0 - 100)
        # Note: A higher drift severity MUST reduce the Drift Health Score
        drift_record = db.query(DriftDetection).filter(DriftDetection.evaluation_id == evaluation_id).first()
        if drift_record:
            raw_drift = float(drift_record.drift_score)
            # PSI mapping: PSI 0.0 -> Health 100; PSI 0.25 -> Health 50; PSI >= 0.50 -> Health 0
            drift_health_score = max(0.0, min(100.0, 100.0 - (raw_drift * 200.0)))
        else:
            drift_health_score = 100.0

        # Composite Overall Reliability Score
        overall_score = (
            (ReliabilityService.WEIGHT_DATA_QUALITY * data_quality_score) +
            (ReliabilityService.WEIGHT_MODEL_PERF * model_perf_score) +
            (ReliabilityService.WEIGHT_DRIFT_HEALTH * drift_health_score)
        )
        overall_score = round(max(0.0, min(100.0, overall_score)), 2)

        # Rating determination
        if overall_score >= 80.0:
            rating = "HIGH"
        elif overall_score >= 60.0:
            rating = "MEDIUM"
        else:
            rating = "LOW"

        # Check existing record
        existing = db.query(ReliabilityScore).filter(ReliabilityScore.evaluation_id == evaluation_id).first()
        if existing:
            existing.data_quality_score = Decimal(str(round(data_quality_score, 2)))
            existing.model_performance_score = Decimal(str(round(model_perf_score, 2)))
            existing.drift_score = Decimal(str(round(drift_health_score, 2)))
            existing.overall_score = Decimal(str(overall_score))
            existing.rating = rating
            rel_obj = existing
        else:
            rel_obj = ReliabilityScore(
                evaluation_id=evaluation_id,
                data_quality_score=Decimal(str(round(data_quality_score, 2))),
                model_performance_score=Decimal(str(round(model_perf_score, 2))),
                drift_score=Decimal(str(round(drift_health_score, 2))),
                overall_score=Decimal(str(overall_score)),
                rating=rating
            )
            db.add(rel_obj)

        db.commit()
        db.refresh(rel_obj)
        return rel_obj

    @staticmethod
    def generate_diagnostic_reasons_and_recommendations(
        data_quality_score: float,
        model_perf_score: float,
        drift_health_score: float,
        overall_score: float,
        rating: str
    ) -> tuple[list[str], list[str]]:
        """
        Produces human-readable diagnostic analysis and actionable recommendations.
        """
        reasons = []
        recommendations = []

        # Data quality diagnostic
        if data_quality_score >= 90.0:
            reasons.append(f"Data quality is strong ({data_quality_score:.1f}/100) with minimal missing or duplicate values.")
        elif data_quality_score >= 70.0:
            reasons.append(f"Data quality is moderate ({data_quality_score:.1f}/100); minor missing values or anomalies exist.")
            recommendations.append("Investigate missing value imputation and cleanse outliers in the incoming dataset.")
        else:
            reasons.append(f"Data quality issues detected ({data_quality_score:.1f}/100); high nullity, schema mismatch, or duplicates present.")
            recommendations.append("Halt deployment until data pipeline cleanses missing fields and eliminates duplicate records.")

        # Model performance diagnostic
        if model_perf_score >= 85.0:
            reasons.append(f"Model performance is excellent ({model_perf_score:.1f}/100) across accuracy and F1 score.")
        elif model_perf_score >= 65.0:
            reasons.append(f"Model performance is acceptable ({model_perf_score:.1f}/100), but precision or recall can be optimized.")
            recommendations.append("Tune classification threshold or experiment with ensemble methods (e.g. Random Forest).")
        else:
            reasons.append(f"Model performance is low ({model_perf_score:.1f}/100), exhibiting substantial classification errors.")
            recommendations.append("Review feature engineering, address class imbalance, or try non-linear algorithms.")

        # Drift health diagnostic
        if drift_health_score >= 85.0:
            reasons.append(f"Data distribution is stable ({drift_health_score:.1f}/100 drift health) compared to the baseline.")
        elif drift_health_score >= 50.0:
            reasons.append(f"Moderate population distribution shift detected ({drift_health_score:.1f}/100 drift health).")
            recommendations.append("Monitor feature stability and schedule retraining if performance begins decaying.")
        else:
            reasons.append(f"Significant feature drift detected ({drift_health_score:.1f}/100 drift health); population has materially shifted.")
            recommendations.append("Immediate retraining required: current production data no longer matches model training distribution.")

        # Overall summary recommendation
        if rating == "HIGH":
            recommendations.append("System is verified reliable and approved for production inference.")
        elif rating == "MEDIUM":
            recommendations.append("System is moderately reliable; review warnings before automated decision-making.")
        else:
            recommendations.append("System reliability is LOW. Action required on highlighted data or model deficiencies.")

        return reasons, recommendations
