# AI Model Evaluation & Data Reliability Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.3-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-grade, full-stack database and machine learning platform that centralizes model versioning, dataset snapshot tracking, automated data quality scoring, Scikit-learn classification evaluation, Population Stability Index (PSI) drift detection, and composite reliability scoring.

Developed as an academic DBMS project at **PES University** by **Mohammed Adaan Hamad (PES2UG24CS279)** and **Navya Kishore Dash (PES2UG24CS307)**, built to production standards for technical interviews and open-source portfolio demonstration.

---

## Key Highlights

- **Authoritative 12-Entity Relational Database:** Implements the complete approved DBMS submission schema in MySQL 8.0 with strict primary keys, foreign keys, unique constraints, check constraints, cascade behaviors, and B-Tree indexes.
- **Automated Data Quality Engine:** 6 deterministic algorithms profiling missingness, uniqueness, data types, numerical ranges (IQR), categorical validity, and schema integrity against raw CSV files.
- **Leak-Free ML Pipeline:** Scikit-learn `Pipeline` and `ColumnTransformer` with stratified train/test splitting, supporting Logistic Regression, Random Forest, and Decision Trees with Joblib artifact serialization.
- **Explainable Drift Detection:** Computes Population Stability Index (PSI) and Kolmogorov-Smirnov 2-sample tests to pinpoint covariate shifts across version iterations before accuracy decay occurs.
- **Signature Reliability Index:** Unifies data quality, model performance, and drift health into a transparent composite rating:
  $$\text{Overall Reliability} = (0.35 \times \text{Data Quality}) + (0.45 \times \text{Model Performance}) + (0.20 \times \text{Drift Health})$$
- **Enterprise SaaS Dashboard:** Responsive React 18 interface with interactive Recharts visual trends, confusion matrix heat maps, dataset comparison matrices, and downloadable audit reports (CSV/JSON).

---

## Architecture Overview

```
+-------------------------------------------------------------------------------+
|                       REACT ENTERPRISE DASHBOARD                              |
|          (Vite + Tailwind CSS + Recharts + Lucide Icons)                      |
|                                                                               |
|  [Overview]  [Datasets]  [Versions]  [Quality]  [Models]  [Evaluations]       |
|  [Comparison]  [Drift Monitoring]  [Reliability Reports]  [DBMS About]        |
+---------------------------------------+---------------------------------------+
                                        | REST API (JSON / Multipart Forms)
                                        v
+-------------------------------------------------------------------------------+
|                         FASTAPI BACKEND SERVICE                               |
|                       (Python 3.12 + SQLAlchemy 2.0)                          |
|                                                                               |
|  - 10 Domain Routers      - Pydantic v2 Validation    - Connection Pooling    |
|  - Pandas Profiling       - Scikit-learn Pipelines    - Joblib Serialization  |
|  - PSI Drift Engine       - Quality Runner            - Reliability Engine    |
+---------------------------------------+---------------------------------------+
                                        | PyMySQL Binary Wire Protocol
                                        v
+-------------------------------------------------------------------------------+
|                        MYSQL 8.0 DATABASE ENGINE                              |
|                                                                               |
|   1. USER                  5. DATA_QUALITY_CHECK        9. EVALUATION_RUN     |
|   2. DATA_SOURCE           6. DATA_QUALITY_RESULT      10. EVALUATION_RESULT  |
|   3. DATASET               7. AI_MODEL                 11. DRIFT_DETECTION    |
|   4. DATASET_VERSION       8. MODEL_VERSION            12. RELIABILITY_SCORE  |
|                                                                               |
|   + 4 Analytical Reporting Views (Leaderboards, Drift Alerts, Quality Stats)  |
+-------------------------------------------------------------------------------+
```

---

## The 12 Core Relational Entities

1. `USER`: Data scientists, ML engineers, and owners (`user_id`, `name`, `email`, `role`, `department`).
2. `DATA_SOURCE`: Ingestion origins (`source_id`, `source_name`, `source_type`, `location`).
3. `DATASET`: Logical business dataset domains (`dataset_id`, `dataset_name`, `source_id`, `owner_id`).
4. `DATASET_VERSION`: Immutable versioned CSV snapshots (`dataset_version_id`, `dataset_id`, `version_number`, `record_count`).
5. `DATA_QUALITY_CHECK`: Defined quality rules & thresholds (`quality_check_id`, `dataset_id`, `check_name`, `check_type`, `threshold`).
6. `DATA_QUALITY_RESULT`: Deterministic execution scores & statuses (`quality_result_id`, `check_id`, `version_id`, `score`, `status`).
7. `AI_MODEL`: Model architecture registry (`model_id`, `model_name`, `model_type`, `owner_id`).
8. `MODEL_VERSION`: Algorithmic iterations (`model_version_id`, `model_id`, `version_number`, `algorithm`).
9. `EVALUATION_RUN`: Central operational hub (`evaluation_id`, `model_version_id`, `dataset_version_id`, `executed_by`, `status`).
10. `EVALUATION_RESULT`: Consolidated metrics (`result_id`, `evaluation_id`, `accuracy`, `precision_score`, `recall_score`, `f1_score`).
11. `DRIFT_DETECTION`: Statistical distribution shift measurements (`drift_id`, `evaluation_id`, `drift_score`, `drift_status`).
12. `RELIABILITY_SCORE`: Holistic governance index (`reliability_id`, `evaluation_id`, `dq_score`, `model_score`, `drift_score`, `overall_score`, `rating`).

---

## Quickstart Guide

### 1. Database Setup (MySQL 8.0)
Create the database and execute the schema:
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/views.sql
```

### 2. Backend Setup
```bash
cd backend

# Create .env from example
cp .env.example .env

# Install Python dependencies
pip install -r requirements.txt

# Populate realistic demo datasets and run real Scikit-learn evaluations
python seed_data.py

# Run the automated test suite (16 tests)
python -m pytest

# Start the FastAPI backend server
uvicorn app.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Launch development server
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## Demo Scenarios Included in Seed

When you run `python seed_data.py`, the system creates real business scenarios:
1. **Financial Fraud Sentinel (v1.0 Logistic Regression, v2.0 Random Forest):** Evaluated against baseline transactions (`v1.0`) achieving $>84\%$ accuracy and $92$ Reliability (`HIGH`).
2. **Drift Attack Test (Fraud Sentinel v2.0 on Drifted Data v2.0):** Evaluated on a version with shifted amounts and foreign locations. Accuracy drops to $72.33\%$, PSI spikes to $0.2620$ (`HIGH DRIFT`), and overall reliability drops to $66.88$ (`MEDIUM`), triggering diagnostic retraining recommendations.
3. **Subscriber Retention Predictor (Customer Churn v1.0 & v1.1):** Comparing linear baseline vs ensemble tree classification across subscriber tiers.

---

## Documentation Directory

The project includes 10 comprehensive documentation guides in `/docs`:
- [`PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) — Problem statement, objectives, and differentiators.
- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Detailed request/response flow and system boundaries.
- [`DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) — Detailed table specs, cardinalities, and 3NF normalization.
- [`ER_DIAGRAM.md`](docs/ER_DIAGRAM.md) — Official Mermaid entity-relationship diagram.
- [`API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) — Complete REST endpoint reference.
- [`ML_METHODOLOGY.md`](docs/ML_METHODOLOGY.md) — Pipeline design, class imbalance handling, and Scikit-learn architecture.
- [`RELIABILITY_FORMULA.md`](docs/RELIABILITY_FORMULA.md) — Mathematical rationale and numerical step-by-step examples.
- [`SETUP_GUIDE.md`](docs/SETUP_GUIDE.md) — Installation manual from clean machine to running servers.
- [`VIVA_PREPARATION.md`](docs/VIVA_PREPARATION.md) — **42 Viva Voce & Technical Interview questions & answers.**
- [`LEARNING_ROADMAP.md`](docs/LEARNING_ROADMAP.md) — 12-phase curriculum and file-by-file codebase walkthrough.

---

## Suggested Git Commit Plan

To publish cleanly to GitHub, follow this structured commit progression:
```bash
git init
git add .gitignore
git commit -m "chore: initialize project structure and gitignore"

git add database/ docs/ER_DIAGRAM.md docs/DATABASE_DESIGN.md
git commit -m "feat(db): establish 12-entity schema, analytical views, and useful queries"

git add backend/
git commit -m "feat(backend): implement FastAPI service, ORM models, ML pipeline, drift engine, and tests"

git add frontend/
git commit -m "feat(frontend): build enterprise React analytics dashboard with Recharts"

git add docs/ README.md
git commit -m "docs: finalize comprehensive viva preparation, learning roadmap, and architecture guides"
```

---

## Academic Information

- **Institution:** PES University
- **Course:** Database Management Systems (DBMS) Laboratory Project
- **Lead Developer:** Mohammed Adaan Hamad (`PES2UG24CS279`)
- **Co-Developer:** Navya Kishore Dash (`PES2UG24CS307`)
- **Baseline Document:** `279_307.pdf`
