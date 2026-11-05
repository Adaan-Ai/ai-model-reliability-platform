# System Architecture & Technical Design

## 1. High-Level Architectural Pattern

The platform is engineered as a **well-factored, modular monolith** comprising three decoupled tiers:
1. **Frontend Presentation Tier (React + Vite + Tailwind CSS):** A responsive, state-driven single-page enterprise dashboard providing interactive charts (Recharts), CSV upload handling, and tabular audit logs.
2. **Backend Application & Analytics Tier (FastAPI + SQLAlchemy + Scikit-learn):** An asynchronous REST API framework orchestrating business logic, leak-free ML pipelines, statistical drift routines, and transaction lifecycles.
3. **Database Tier (MySQL Server 8.0):** The authoritative source of truth enforcing relational constraints, composite foreign keys, check constraints, analytical views, and normalized schema integrity.

```
+-------------------------------------------------------------------------------+
|                             ENTERPRISE FRONTEND                               |
|              (React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts)       |
|                                                                               |
|  [Dashboard]  [Datasets]  [Versions]  [Quality]  [Models]  [Evaluations]      |
|  [Model Comparison]  [Drift Monitoring]  [Reliability Reports]  [DBMS About]  |
+---------------------------------------+---------------------------------------+
                                        |  REST API (JSON / Multipart Forms)
                                        v
+-------------------------------------------------------------------------------+
|                              FASTAPI BACKEND                                  |
|                             (Python 3.12 Core)                                |
|                                                                               |
|  +---------------------+   +---------------------+   +---------------------+  |
|  |     Routers Tier    |   |     Schemas Tier    |   |     Services Tier   |  |
|  |  (10 Domain Routers)|   |  (Pydantic Models)  |   |  (Business Engines) |  |
|  +----------+----------+   +---------------------+   +----------+----------+  |
|             |                                                   |             |
|             v                                                   v             |
|  +-------------------------------------------------------------------------+  |
|  |                       ANALYTICS & ML ENGINE                             |  |
|  |  - Pandas Profiling (Record count, types, missingness, duplicates)      |  |
|  |  - Quality Service (Deterministic scoring on raw CSV files)             |  |
|  |  - Evaluation Pipeline (Scikit-learn ColumnTransformer, Stratified Split)| |
|  |  - Classifiers (Logistic Regression, Random Forest, Decision Tree)      |  |
|  |  - Drift Service (Population Stability Index + KS 2-sample tests)       |  |
|  |  - Reliability Service (Weighted Composite: 0.35 DQ + 0.45 Perf + 0.20 D)|  |
|  +-------------------------------------------------------------------------+  |
+---------------------------------------+---------------------------------------+
                                        |  SQLAlchemy 2.0 ORM + PyMySQL Driver
                                        v
+-------------------------------------------------------------------------------+
|                            MYSQL 8.0 DATABASE                                 |
|                       (ai_model_reliability Database)                         |
|                                                                               |
|   1. USER                  5. DATA_QUALITY_CHECK        9. EVALUATION_RUN     |
|   2. DATA_SOURCE           6. DATA_QUALITY_RESULT      10. EVALUATION_RESULT  |
|   3. DATASET               7. AI_MODEL                 11. DRIFT_DETECTION    |
|   4. DATASET_VERSION       8. MODEL_VERSION            12. RELIABILITY_SCORE  |
|                                                                               |
|   + 4 Analytical Views: view_evaluation_overview, view_dataset_quality_summary|
|                         view_model_leaderboard, view_drift_alerts             |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                             PERSISTENT STORAGE                                |
|   /storage/datasets/   -> Versioned immutable CSV files                       |
|   /storage/models/     -> Serialized Scikit-learn pipelines (.joblib)         |
|   /storage/reports/    -> Detailed JSON audit trails and CSV export summaries |
+-------------------------------------------------------------------------------+
```

---

## 2. Request / Response Lifecycle

Here is the exact lifecycle when a user triggers an evaluation:

1. **User Action:** The user selects Model Version `Financial Fraud Sentinel v2.0 (Random Forest)`, Dataset Version `Bank Transaction Fraud Stream v2.0`, and Target Column `is_fraud`, clicking "Execute Model Evaluation".
2. **HTTP Dispatch:** The frontend sends a `POST /api/evaluations` request with the JSON payload to the FastAPI backend.
3. **Pydantic Validation:** `EvaluationRunCreate` validates that the payload has positive IDs, a test size between $0.05$ and $0.50$, and valid seed parameters.
4. **Session Acquisition:** The `get_db()` dependency borrows a MySQL connection from SQLAlchemy's connection pool.
5. **Initial Run Creation:** An `EVALUATION_RUN` record is inserted with `status = 'RUNNING'`.
6. **Data Ingestion:** `EvaluationService` safely resolves the dataset version path (`storage/datasets/dataset_1_v2.0.csv`) and loads it into a Pandas DataFrame.
7. **Leak-Free Preprocessing:**
   - Numerical columns (`amount`, `old_balance`, `new_balance`) are piped into `SimpleImputer(strategy='median')` and `StandardScaler()`.
   - Categorical columns (`transaction_type`, `device_type`, `location`) are piped into `SimpleImputer(strategy='most_frequent')` and `OneHotEncoder(handle_unknown='ignore')`.
   - The preprocessor and classifier are bundled in a Scikit-learn `Pipeline`.
8. **Model Fitting:** `clf_pipeline.fit(X_train, y_train)` fits strictly on training data.
9. **Metric Computation:** Predictions on the test set yield Accuracy, Precision (weighted), Recall (weighted), and F1-score (weighted), as well as the confusion matrix.
10. **Artifact Serialization:** `joblib.dump(clf_pipeline, path)` serializes the trained model into `storage/models/model_version_2.joblib`.
11. **Drift Detection:** `DriftService` locates the prior dataset version (`v1.0`), extracts shared features, calculates Population Stability Index (PSI) and Kolmogorov-Smirnov $p$-values, and persists results to `drift_detection`.
12. **Reliability Scoring:** `ReliabilityService` calculates Data Quality score from `data_quality_result`, Model Performance score from Accuracy and F1, and Drift Health score from PSI. The composite score and rating (`HIGH`, `MEDIUM`, or `LOW`) are saved to `reliability_score`.
13. **Status Update & Report:** `EVALUATION_RUN.status` is updated to `'COMPLETED'`, a full JSON audit report is saved to `storage/reports/`, and the complete response is returned to the frontend.
14. **UI Render:** The React application receives the response, renders metric cards, plots the confusion matrix heat map, displays diagnostic recommendations, and updates dashboard charts.

---

## 3. Communication Protocols & Data Contracts

- **Client to Server:** JSON over HTTP/1.1 with CORS protection. File uploads use `multipart/form-data`.
- **Server to Database:** PyMySQL binary wire protocol connecting to MySQL 8.0 on TCP port 3306 with UTF-8 (`utf8mb4`) character encoding.
- **Connection Management:** SQLAlchemy connection pooling with `pool_pre_ping=True` and `pool_recycle=3600` to prevent stale socket errors.
