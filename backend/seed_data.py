"""
Seed Data Generator
Generates reproducible synthetic business datasets (Fraud Detection & Churn Prediction),
saves real CSV snapshots into `storage/datasets/`, creates the 12 core entity records in MySQL,
and executes REAL data quality checks and Scikit-learn ML evaluations.
"""

import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from app.config import settings
from app.database import engine, SessionLocal, Base
from app.models import (
    User, DataSource, Dataset, DatasetVersion,
    DataQualityCheck, AIModel, ModelVersion,
    EvaluationRun, EvaluationResult, DriftDetection, ReliabilityScore
)
from app.services.dataset_service import DatasetService
from app.services.quality_service import QualityService
from app.services.evaluation_service import EvaluationService
from app.schemas.evaluation import EvaluationRunCreate

def generate_fraud_datasets():
    """
    Generates Bank Transaction Fraud Detection datasets:
    - Version 1.0 (Baseline distribution, ~1200 records)
    - Version 2.0 (Drifted distribution with shifted amounts and foreign locations, ~1500 records)
    """
    np.random.seed(42)

    # --- Version 1.0 (Baseline) ---
    n_v1 = 1200
    amounts_v1 = np.random.exponential(scale=180.0, size=n_v1) + 10.0
    old_bal_v1 = np.random.uniform(100.0, 15000.0, size=n_v1)
    new_bal_v1 = np.maximum(0.0, old_bal_v1 - amounts_v1 * np.random.uniform(0.7, 1.2, size=n_v1))
    
    types_v1 = np.random.choice(["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT"], size=n_v1, p=[0.45, 0.25, 0.20, 0.10])
    devices_v1 = np.random.choice(["MOBILE", "WEB", "POS"], size=n_v1, p=[0.50, 0.35, 0.15])
    locations_v1 = np.random.choice(["Domestic", "International"], size=n_v1, p=[0.90, 0.10])

    # Fraud logic with correlation to high amounts and transfers
    fraud_prob_v1 = (
        (amounts_v1 > 350.0).astype(float) * 0.25 +
        (types_v1 == "TRANSFER").astype(float) * 0.30 +
        (locations_v1 == "International").astype(float) * 0.30
    )
    fraud_prob_v1 = np.clip(fraud_prob_v1, 0.02, 0.85)
    is_fraud_v1 = (np.random.rand(n_v1) < fraud_prob_v1).astype(int)

    df_v1 = pd.DataFrame({
        "transaction_id": [f"TXN_{10000 + i}" for i in range(n_v1)],
        "amount": np.round(amounts_v1, 2),
        "old_balance": np.round(old_bal_v1, 2),
        "new_balance": np.round(new_bal_v1, 2),
        "transaction_type": types_v1,
        "device_type": devices_v1,
        "location": locations_v1,
        "is_fraud": is_fraud_v1
    })

    # Inject realistic slight data anomalies (missing values and duplicates)
    mask_null_amount = np.random.rand(n_v1) < 0.015
    df_v1.loc[mask_null_amount, "amount"] = np.nan
    mask_null_loc = np.random.rand(n_v1) < 0.02
    df_v1.loc[mask_null_loc, "location"] = np.nan

    # Duplicate 15 rows to test duplicate check
    dup_rows = df_v1.iloc[10:25].copy()
    df_v1 = pd.concat([df_v1, dup_rows], ignore_index=True)

    # --- Version 2.0 (Drifted) ---
    # Shifted: significantly higher transactions, more International traffic, higher CASH_OUT
    np.random.seed(101)
    n_v2 = 1500
    amounts_v2 = np.random.exponential(scale=350.0, size=n_v2) + 25.0  # Drift in amounts
    old_bal_v2 = np.random.uniform(50.0, 20000.0, size=n_v2)
    new_bal_v2 = np.maximum(0.0, old_bal_v2 - amounts_v2 * np.random.uniform(0.6, 1.4, size=n_v2))

    types_v2 = np.random.choice(["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT"], size=n_v2, p=[0.25, 0.35, 0.35, 0.05])
    devices_v2 = np.random.choice(["MOBILE", "WEB", "POS"], size=n_v2, p=[0.75, 0.20, 0.05])
    locations_v2 = np.random.choice(["Domestic", "International"], size=n_v2, p=[0.65, 0.35])  # Major shift!

    fraud_prob_v2 = (
        (amounts_v2 > 450.0).astype(float) * 0.30 +
        (types_v2 == "TRANSFER").astype(float) * 0.25 +
        (locations_v2 == "International").astype(float) * 0.35
    )
    fraud_prob_v2 = np.clip(fraud_prob_v2, 0.03, 0.90)
    is_fraud_v2 = (np.random.rand(n_v2) < fraud_prob_v2).astype(int)

    df_v2 = pd.DataFrame({
        "transaction_id": [f"TXN_{30000 + i}" for i in range(n_v2)],
        "amount": np.round(amounts_v2, 2),
        "old_balance": np.round(old_bal_v2, 2),
        "new_balance": np.round(new_bal_v2, 2),
        "transaction_type": types_v2,
        "device_type": devices_v2,
        "location": locations_v2,
        "is_fraud": is_fraud_v2
    })

    return df_v1, df_v2

def generate_churn_datasets():
    """
    Generates Customer Churn datasets:
    - Version 1.0 (~1000 records)
    - Version 1.1 (~1100 records)
    """
    np.random.seed(77)
    n = 1000
    tenure = np.random.randint(1, 72, size=n)
    monthly = np.random.uniform(20.0, 115.0, size=n)
    total = tenure * monthly * np.random.uniform(0.9, 1.05, size=n)
    contract = np.random.choice(["Month-to-month", "One year", "Two year"], size=n, p=[0.55, 0.25, 0.20])
    payment = np.random.choice(["Electronic check", "Bank transfer", "Credit card"], size=n, p=[0.40, 0.35, 0.25])
    internet = np.random.choice(["DSL", "Fiber optic", "No"], size=n, p=[0.40, 0.45, 0.15])

    # Churn probability higher with month-to-month and electronic check
    churn_prob = (
        (contract == "Month-to-month").astype(float) * 0.35 +
        (internet == "Fiber optic").astype(float) * 0.25 +
        (tenure < 12).astype(float) * 0.20
    )
    churn_prob = np.clip(churn_prob, 0.05, 0.85)
    churn = (np.random.rand(n) < churn_prob).astype(int)

    df_v1 = pd.DataFrame({
        "customer_id": [f"CUST_{5000 + i}" for i in range(n)],
        "tenure_months": tenure,
        "monthly_charges": np.round(monthly, 2),
        "total_charges": np.round(total, 2),
        "contract_type": contract,
        "payment_method": payment,
        "internet_service": internet,
        "churn": churn
    })

    # Version 1.1: slightly updated
    df_v2 = df_v1.sample(n=850, random_state=42).copy()
    extra_n = 250
    extra_tenure = np.random.randint(1, 72, size=extra_n)
    extra_monthly = np.random.uniform(25.0, 118.0, size=extra_n)
    extra_total = extra_tenure * extra_monthly
    extra_contract = np.random.choice(["Month-to-month", "One year", "Two year"], size=extra_n, p=[0.50, 0.28, 0.22])
    extra_payment = np.random.choice(["Electronic check", "Bank transfer", "Credit card"], size=extra_n, p=[0.38, 0.37, 0.25])
    extra_internet = np.random.choice(["DSL", "Fiber optic", "No"], size=extra_n, p=[0.38, 0.48, 0.14])
    extra_churn = (np.random.rand(extra_n) < 0.28).astype(int)

    df_extra = pd.DataFrame({
        "customer_id": [f"CUST_{8000 + i}" for i in range(extra_n)],
        "tenure_months": extra_tenure,
        "monthly_charges": np.round(extra_monthly, 2),
        "total_charges": np.round(extra_total, 2),
        "contract_type": extra_contract,
        "payment_method": extra_payment,
        "internet_service": extra_internet,
        "churn": extra_churn
    })
    df_v2 = pd.concat([df_v2, df_extra], ignore_index=True)

    return df_v1, df_v2

def run_seed():
    print("=" * 70)
    print("[SEED] AI MODEL EVALUATION & DATA RELIABILITY PLATFORM - SEED GENERATOR")
    print("=" * 70)

    db: Session = SessionLocal()

    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already contains data. Cleaning up tables for clean reproducible seed...")
            # Truncate / delete records safely adhering to foreign keys
            db.query(ReliabilityScore).delete()
            db.query(DriftDetection).delete()
            db.query(EvaluationResult).delete()
            db.query(EvaluationRun).delete()
            db.query(DataQualityResult).delete()
            db.query(DataQualityCheck).delete()
            db.query(ModelVersion).delete()
            db.query(AIModel).delete()
            db.query(DatasetVersion).delete()
            db.query(Dataset).delete()
            db.query(DataSource).delete()
            db.query(User).delete()
            db.commit()

        # 1. Seed USERS
        print("\n1. Creating Demo Users...")
        u1 = User(name="Mohammed Adaan Hamad", email="adaan@pesu.edu", role="Lead Engineer", department="Data Science")
        u2 = User(name="Navya Kishore Dash", email="navya@pesu.edu", role="Co-Engineer", department="Data Platform")
        u3 = User(name="Dr. Deena Hijam", email="deena.hijam@pesu.edu", role="Faculty Advisor", department="Computer Science")
        db.add_all([u1, u2, u3])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)
        print(f"   Created users: {u1.name} (ID: {u1.user_id}), {u2.name} (ID: {u2.user_id})")

        # 2. Seed DATA_SOURCES
        print("\n2. Creating Data Sources...")
        ds1 = DataSource(source_name="Core Banking Transaction Lake", source_type="S3 Data Lake", location="s3://pesu-banking-data/transactions/")
        ds2 = DataSource(source_name="Customer CRM Data Warehouse", source_type="PostgreSQL", location="postgresql://dw.internal:5432/crm_prod")
        db.add_all([ds1, ds2])
        db.commit()
        db.refresh(ds1)
        db.refresh(ds2)
        print(f"   Created sources: {ds1.source_name}, {ds2.source_name}")

        # 3. Seed DATASETS & DATASET_VERSIONS
        print("\n3. Generating Real Business Datasets & Saving CSVs...")
        fraud_v1_df, fraud_v2_df = generate_fraud_datasets()
        churn_v1_df, churn_v2_df = generate_churn_datasets()

        # Dataset 1: Bank Transactions Fraud
        d1 = Dataset(
            dataset_name="Bank Transaction Fraud Stream",
            description="High-frequency financial transaction records with fraud labels for risk assessment.",
            source_id=ds1.source_id,
            owner_id=u1.user_id,
            created_date=date.today() - timedelta(days=30)
        )
        db.add(d1)
        db.commit()
        db.refresh(d1)

        # Save Fraud v1.0
        v1_path = DatasetService.get_storage_path(d1.dataset_id, "1.0")
        fraud_v1_df.to_csv(v1_path, index=False)
        dv1_1 = DatasetVersion(
            dataset_id=d1.dataset_id,
            version_number="1.0",
            record_count=len(fraud_v1_df),
            created_date=date.today() - timedelta(days=20)
        )
        db.add(dv1_1)
        db.commit()
        db.refresh(dv1_1)

        # Save Fraud v2.0 (drifted)
        v2_path = DatasetService.get_storage_path(d1.dataset_id, "2.0")
        fraud_v2_df.to_csv(v2_path, index=False)
        dv1_2 = DatasetVersion(
            dataset_id=d1.dataset_id,
            version_number="2.0",
            record_count=len(fraud_v2_df),
            created_date=date.today() - timedelta(days=5)
        )
        db.add(dv1_2)
        db.commit()
        db.refresh(dv1_2)

        # Dataset 2: Customer Churn
        d2 = Dataset(
            dataset_name="Customer Subscription & Churn",
            description="Telecom subscriber engagement metrics, contract structures, and monthly revenue.",
            source_id=ds2.source_id,
            owner_id=u2.user_id,
            created_date=date.today() - timedelta(days=45)
        )
        db.add(d2)
        db.commit()
        db.refresh(d2)

        # Save Churn v1.0
        cv1_path = DatasetService.get_storage_path(d2.dataset_id, "1.0")
        churn_v1_df.to_csv(cv1_path, index=False)
        dv2_1 = DatasetVersion(
            dataset_id=d2.dataset_id,
            version_number="1.0",
            record_count=len(churn_v1_df),
            created_date=date.today() - timedelta(days=35)
        )
        db.add(dv2_1)
        db.commit()
        db.refresh(dv2_1)

        # Save Churn v1.1
        cv2_path = DatasetService.get_storage_path(d2.dataset_id, "1.1")
        churn_v2_df.to_csv(cv2_path, index=False)
        dv2_2 = DatasetVersion(
            dataset_id=d2.dataset_id,
            version_number="1.1",
            record_count=len(churn_v2_df),
            created_date=date.today() - timedelta(days=10)
        )
        db.add(dv2_2)
        db.commit()
        db.refresh(dv2_2)

        print(f"   Created Dataset '{d1.dataset_name}' (v1.0: {len(fraud_v1_df)} rows, v2.0: {len(fraud_v2_df)} rows)")
        print(f"   Created Dataset '{d2.dataset_name}' (v1.0: {len(churn_v1_df)} rows, v1.1: {len(churn_v2_df)} rows)")

        # 4. DATA QUALITY CHECKS & RESULTS
        print("\n4. Initializing and Executing Real Data Quality Checks...")
        DatasetService.create_default_quality_checks(db, d1.dataset_id)
        DatasetService.create_default_quality_checks(db, d2.dataset_id)

        # Run quality checks on all 4 versions
        q_res1 = QualityService.run_checks_for_version(db, dv1_1.dataset_version_id)
        q_res2 = QualityService.run_checks_for_version(db, dv1_2.dataset_version_id)
        q_res3 = QualityService.run_checks_for_version(db, dv2_1.dataset_version_id)
        q_res4 = QualityService.run_checks_for_version(db, dv2_2.dataset_version_id)
        print(f"   Executed {len(q_res1) + len(q_res2) + len(q_res3) + len(q_res4)} real data quality checks.")

        # 5. Seed AI MODELS & MODEL VERSIONS
        print("\n5. Registering AI Models & Algorithmic Versions...")
        m1 = AIModel(
            model_name="Financial Fraud Sentinel",
            model_type="Classification",
            description="Predicts likelihood of fraudulent financial transactions to mitigate financial crimes.",
            owner_id=u1.user_id,
            created_date=date.today() - timedelta(days=25)
        )
        db.add(m1)
        db.commit()
        db.refresh(m1)

        mv1_1 = ModelVersion(model_id=m1.model_id, version_number="1.0", algorithm="Logistic Regression", created_date=date.today() - timedelta(days=22))
        mv1_2 = ModelVersion(model_id=m1.model_id, version_number="2.0", algorithm="Random Forest", created_date=date.today() - timedelta(days=15))
        mv1_3 = ModelVersion(model_id=m1.model_id, version_number="3.0", algorithm="Decision Tree", created_date=date.today() - timedelta(days=7))
        db.add_all([mv1_1, mv1_2, mv1_3])
        db.commit()
        db.refresh(mv1_1)
        db.refresh(mv1_2)
        db.refresh(mv1_3)

        m2 = AIModel(
            model_name="Subscriber Retention Predictor",
            model_type="Classification",
            description="Predicts subscriber churn probabilities based on tenure, service tier, and billing behavior.",
            owner_id=u2.user_id,
            created_date=date.today() - timedelta(days=40)
        )
        db.add(m2)
        db.commit()
        db.refresh(m2)

        mv2_1 = ModelVersion(model_id=m2.model_id, version_number="1.0", algorithm="Logistic Regression", created_date=date.today() - timedelta(days=30))
        mv2_2 = ModelVersion(model_id=m2.model_id, version_number="2.0", algorithm="Random Forest", created_date=date.today() - timedelta(days=12))
        db.add_all([mv2_1, mv2_2])
        db.commit()
        db.refresh(mv2_1)
        db.refresh(mv2_2)

        print(f"   Registered Model '{m1.model_name}' (3 versions: Logistic Regression, Random Forest, Decision Tree)")
        print(f"   Registered Model '{m2.model_name}' (2 versions: Logistic Regression, Random Forest)")

        # 6. EXECUTE REAL MODEL EVALUATIONS
        print("\n6. Running Real Scikit-learn Model Evaluations & Generating Metrics...")

        # Run 1: Fraud Model v1.0 on Fraud Dataset v1.0
        print("   -> Evaluating Fraud Sentinel v1.0 (Logistic Regression) on Fraud Data v1.0...")
        eval1 = EvaluationService.run_evaluation(
            db,
            EvaluationRunCreate(
                model_version_id=mv1_1.model_version_id,
                dataset_version_id=dv1_1.dataset_version_id,
                executed_by=u1.user_id,
                target_column="is_fraud",
                random_state=42
            )
        )

        # Run 2: Fraud Model v2.0 on Fraud Dataset v1.0
        print("   -> Evaluating Fraud Sentinel v2.0 (Random Forest) on Fraud Data v1.0...")
        eval2 = EvaluationService.run_evaluation(
            db,
            EvaluationRunCreate(
                model_version_id=mv1_2.model_version_id,
                dataset_version_id=dv1_1.dataset_version_id,
                executed_by=u1.user_id,
                target_column="is_fraud",
                random_state=42
            )
        )

        # Run 3: Fraud Model v2.0 on Fraud Dataset v2.0 (DRIFTED DATASET! Triggers real drift calculation against v1.0!)
        print("   -> Evaluating Fraud Sentinel v2.0 (Random Forest) on Fraud Data v2.0 (DRIFT TEST)...")
        eval3 = EvaluationService.run_evaluation(
            db,
            EvaluationRunCreate(
                model_version_id=mv1_2.model_version_id,
                dataset_version_id=dv1_2.dataset_version_id,
                executed_by=u1.user_id,
                target_column="is_fraud",
                random_state=42
            )
        )

        # Run 4: Churn Model v1.0 on Churn Dataset v1.0
        print("   -> Evaluating Churn Predictor v1.0 (Logistic Regression) on Churn Data v1.0...")
        eval4 = EvaluationService.run_evaluation(
            db,
            EvaluationRunCreate(
                model_version_id=mv2_1.model_version_id,
                dataset_version_id=dv2_1.dataset_version_id,
                executed_by=u2.user_id,
                target_column="churn",
                random_state=42
            )
        )

        # Run 5: Churn Model v2.0 on Churn Dataset v1.1
        print("   -> Evaluating Churn Predictor v2.0 (Random Forest) on Churn Data v1.1...")
        eval5 = EvaluationService.run_evaluation(
            db,
            EvaluationRunCreate(
                model_version_id=mv2_2.model_version_id,
                dataset_version_id=dv2_2.dataset_version_id,
                executed_by=u2.user_id,
                target_column="churn",
                random_state=42
            )
        )

        print("\n" + "=" * 70)
        print("[SUCCESS] SEED GENERATION & PIPELINE EVALUATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Evaluations stored in database: 5 completed runs with real metrics.")
        print(f"Check Swagger UI at http://localhost:8000/docs or run pytest tests.")

    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
