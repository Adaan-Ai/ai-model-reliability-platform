"""
Model Evaluation Engine
Executes leak-free Scikit-learn classification pipelines, computes evaluation metrics,
serializes trained model artifacts with Joblib, triggers drift and reliability services,
and writes comprehensive reports.
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.models.model_version import ModelVersion
from app.models.dataset_version import DatasetVersion
from app.models.ai_model import AIModel
from app.schemas.evaluation import EvaluationRunCreate
from app.services.dataset_service import DatasetService
from app.services.drift_service import DriftService
from app.services.reliability_service import ReliabilityService

class EvaluationService:
    @staticmethod
    def run_evaluation(
        db: Session,
        req: EvaluationRunCreate
    ) -> EvaluationRun:
        """
        Executes end-to-end evaluation pipeline with real ML models and Scikit-learn pipelines.
        """
        # 1. Validate Model Version
        model_ver = db.query(ModelVersion).filter(ModelVersion.model_version_id == req.model_version_id).first()
        if not model_ver:
            raise HTTPException(status_code=404, detail="Model version not found.")

        # 2. Validate Dataset Version
        data_ver = db.query(DatasetVersion).filter(DatasetVersion.dataset_version_id == req.dataset_version_id).first()
        if not data_ver:
            raise HTTPException(status_code=404, detail="Dataset version not found.")

        # 3. Create initial EvaluationRun record with RUNNING status
        now = datetime.now()
        eval_run = EvaluationRun(
            model_version_id=req.model_version_id,
            dataset_version_id=req.dataset_version_id,
            executed_by=req.executed_by,
            execution_date=now,
            status="RUNNING"
        )
        db.add(eval_run)
        db.commit()
        db.refresh(eval_run)

        try:
            # 4. Load dataset CSV
            file_path = DatasetService.get_storage_path(data_ver.dataset_id, data_ver.version_number)
            if not file_path.exists():
                raise ValueError(f"Dataset CSV not found at {file_path.name}")

            df = pd.read_csv(file_path)

            if req.target_column not in df.columns:
                raise ValueError(f"Target column '{req.target_column}' does not exist in dataset.")

            # Filter out rows where target is missing
            df = df.dropna(subset=[req.target_column])
            if len(df) < 10:
                raise ValueError("Dataset has insufficient rows for meaningful train/test split.")

            # Identify features
            if req.feature_columns:
                missing_feats = [f for f in req.feature_columns if f not in df.columns]
                if missing_feats:
                    raise ValueError(f"Feature columns not found: {missing_feats}")
                feature_cols = [f for f in req.feature_columns if f != req.target_column]
            else:
                feature_cols = [c for c in df.columns if c != req.target_column]

            if not feature_cols:
                raise ValueError("At least one feature column is required.")

            X = df[feature_cols]
            y = df[req.target_column]

            # Separate numerical and categorical columns
            numerical_cols = list(X.select_dtypes(include=[np.number]).columns)
            categorical_cols = [c for c in feature_cols if c not in numerical_cols]

            # Build leak-free preprocessing pipeline
            numeric_transformer = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            categorical_transformer = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ])

            transformers = []
            if numerical_cols:
                transformers.append(("num", numeric_transformer, numerical_cols))
            if categorical_cols:
                transformers.append(("cat", categorical_transformer, categorical_cols))

            preprocessor = ColumnTransformer(transformers=transformers)

            # Determine classifier algorithm
            algo = (model_ver.algorithm or "Logistic Regression").strip().lower()
            if "random forest" in algo:
                classifier = RandomForestClassifier(n_estimators=100, random_state=req.random_state)
            elif "decision tree" in algo:
                classifier = DecisionTreeClassifier(max_depth=6, random_state=req.random_state)
            else:
                # Default to Logistic Regression
                classifier = LogisticRegression(max_iter=1000, random_state=req.random_state)

            clf_pipeline = Pipeline(steps=[
                ("preprocessor", preprocessor),
                ("classifier", classifier)
            ])

            # Stratified train-test split if class counts allow
            stratify_opt = y if y.value_counts().min() >= 2 else None
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=req.test_size,
                random_state=req.random_state,
                stratify=stratify_opt
            )

            # Fit pipeline strictly on training data (no data leakage)
            clf_pipeline.fit(X_train, y_train)

            # Predict on test set
            y_pred = clf_pipeline.predict(X_test)

            # Calculate metrics
            acc = round(accuracy_score(y_test, y_pred) * 100.0, 2)
            prec = round(precision_score(y_test, y_pred, average="weighted", zero_division=0) * 100.0, 2)
            rec = round(recall_score(y_test, y_pred, average="weighted", zero_division=0) * 100.0, 2)
            f1 = round(f1_score(y_test, y_pred, average="weighted", zero_division=0) * 100.0, 2)

            # Confusion Matrix & Classification Report
            labels = [str(lbl) for lbl in sorted(y.unique())]
            cm = confusion_matrix(y_test, y_pred, labels=sorted(y.unique()))
            cm_list = cm.tolist()
            report_dict = classification_report(y_test, y_pred, labels=sorted(y.unique()), output_dict=True, zero_division=0)

            # Serialize model artifact with Joblib
            model_artifact_path = settings.MODEL_STORAGE_PATH / f"model_version_{model_ver.model_version_id}.joblib"
            joblib.dump(clf_pipeline, model_artifact_path)

            # 5. Persist EVALUATION_RESULT
            eval_result = EvaluationResult(
                evaluation_id=eval_run.evaluation_id,
                accuracy=Decimal(str(acc)),
                precision_score=Decimal(str(prec)),
                recall_score=Decimal(str(rec)),
                f1_score=Decimal(str(f1))
            )
            db.add(eval_result)
            db.commit()

            # 6. Execute Drift Detection
            DriftService.detect_drift_for_evaluation(
                db=db,
                evaluation_id=eval_run.evaluation_id,
                dataset_version_id=req.dataset_version_id
            )

            # 7. Execute Reliability Scoring
            rel_score = ReliabilityService.calculate_reliability(
                db=db,
                evaluation_id=eval_run.evaluation_id
            )

            # 8. Mark EvaluationRun as COMPLETED
            eval_run.status = "COMPLETED"
            db.commit()
            db.refresh(eval_run)

            # 9. Save comprehensive report JSON
            drift_rep = DriftService.get_drift_report(eval_run.evaluation_id)
            reasons, recs = ReliabilityService.generate_diagnostic_reasons_and_recommendations(
                data_quality_score=float(rel_score.data_quality_score),
                model_perf_score=float(rel_score.model_performance_score),
                drift_health_score=float(rel_score.drift_score),
                overall_score=float(rel_score.overall_score),
                rating=rel_score.rating
            )

            full_report = {
                "evaluation_id": eval_run.evaluation_id,
                "model_version_id": model_ver.model_version_id,
                "algorithm": model_ver.algorithm,
                "dataset_version_id": data_ver.dataset_version_id,
                "target_column": req.target_column,
                "feature_columns": feature_cols,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "confusion_matrix": cm_list,
                "class_labels": labels,
                "classification_report": report_dict,
                "drift_summary": drift_rep,
                "reliability_score": float(rel_score.overall_score),
                "reliability_rating": rel_score.rating,
                "reasons": reasons,
                "recommendations": recs
            }
            report_file = settings.REPORT_STORAGE_PATH / f"evaluation_{eval_run.evaluation_id}_report.json"
            with open(report_file, "w") as f:
                json.dump(full_report, f, indent=2)

            return eval_run

        except Exception as e:
            # In case of evaluation error, update status to FAILED
            eval_run.status = "FAILED"
            db.commit()
            db.refresh(eval_run)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {str(e)}"
            )

    @staticmethod
    def get_evaluation_report(evaluation_id: int) -> dict | None:
        report_file = settings.REPORT_STORAGE_PATH / f"evaluation_{evaluation_id}_report.json"
        if report_file.exists():
            with open(report_file, "r") as f:
                return json.load(f)
        return None
