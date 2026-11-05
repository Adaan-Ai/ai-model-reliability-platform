# Master Learning Roadmap & File-by-File Codebase Walkthrough

This roadmap provides a structured 12-phase curriculum designed specifically for a third-year Computer Science student to deeply master every layer of this codebase.

---

## Complete File-by-File Codebase Directory

```
ai-model-reliability-platform/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application setup, CORS, route registration
│   │   ├── config.py                   # Pydantic Settings, environment variables, storage paths
│   │   ├── database.py                 # SQLAlchemy engine, sessionmaker, get_db() dependency
│   │   ├── models/                     # 12 SQLAlchemy ORM models matching MySQL schema
│   │   │   ├── __init__.py             # Exports all 12 models
│   │   │   ├── user.py                 # User model (Entity 1)
│   │   │   ├── data_source.py          # DataSource model (Entity 2)
│   │   │   ├── dataset.py              # Dataset model (Entity 3)
│   │   │   ├── dataset_version.py      # DatasetVersion model (Entity 4)
│   │   │   ├── quality_check.py        # DataQualityCheck model (Entity 5)
│   │   │   ├── quality_result.py       # DataQualityResult model (Entity 6)
│   │   │   ├── ai_model.py             # AIModel model (Entity 7)
│   │   │   ├── model_version.py        # ModelVersion model (Entity 8)
│   │   │   ├── evaluation_run.py       # EvaluationRun central hub model (Entity 9)
│   │   │   ├── evaluation_result.py    # EvaluationResult model (Entity 10)
│   │   │   ├── drift_detection.py      # DriftDetection model (Entity 11)
│   │   │   └── reliability_score.py    # ReliabilityScore model (Entity 12)
│   │   ├── schemas/                    # Pydantic v2 validation and serialization schemas
│   │   │   ├── __init__.py             # Exports all schemas
│   │   │   ├── user.py                 # UserCreate, UserRead
│   │   │   ├── data_source.py          # DataSourceCreate, DataSourceRead
│   │   │   ├── dataset.py              # DatasetCreate, DatasetRead, DatasetVersionRead
│   │   │   ├── quality.py              # QualityCheckCreate, QualityResultRead
│   │   │   ├── model.py                # AIModelCreate, ModelVersionRead
│   │   │   ├── evaluation.py           # EvaluationRunCreate, EvaluationRunRead, EvaluationRunDetail
│   │   │   ├── drift.py                # DriftDetectionRead, FeatureDriftDetail
│   │   │   ├── reliability.py          # ReliabilityScoreRead, ReliabilityReportDetail
│   │   │   └── dashboard.py            # DashboardOverview, TrendPoint, ReliabilityDistribution
│   │   ├── routers/                    # REST API endpoint handlers
│   │   │   ├── __init__.py             # Exports routers
│   │   │   ├── dashboard.py            # Real-time aggregated MySQL KPI endpoints
│   │   │   ├── users.py                # User CRUD
│   │   │   ├── data_sources.py         # Data Source CRUD
│   │   │   ├── datasets.py             # Dataset CRUD, CSV upload, version inspection
│   │   │   ├── quality.py              # Quality checks definition and execution
│   │   │   ├── models.py               # AI Model registry and algorithmic versions
│   │   │   ├── evaluations.py          # Scikit-learn evaluation pipeline trigger and history
│   │   │   ├── drift.py                # Population Stability Index drift reports
│   │   │   ├── reliability.py          # Composite score calculation and formula details
│   │   │   └── reports.py              # Downloadable CSV / JSON audit reports
│   │   └── services/                   # Core business logic and analytical engines
│   │       ├── __init__.py             # Exports services
│   │       ├── dataset_service.py      # CSV validation, secure storage, Pandas profiling
│   │       ├── quality_service.py      # 6 deterministic quality check algorithms
│   │       ├── model_service.py        # Model registration and version helpers
│   │       ├── evaluation_service.py   # Scikit-learn leak-free pipeline, Joblib serialization
│   │       ├── drift_service.py        # Population Stability Index (PSI) & KS test
│   │       └── reliability_service.py  # 3-pillar weighted reliability scoring
│   ├── tests/                          # Automated Pytest suite (16 tests)
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Pytest fixtures and test dataframes
│   │   ├── test_api.py                 # REST endpoint integration tests (TestClient)
│   │   ├── test_drift.py               # PSI calculation tests
│   │   ├── test_quality.py             # Data quality check algorithm tests
│   │   └── test_reliability.py         # Signature reliability formula tests
│   ├── seed_data.py                    # Generates synthetic data, seeds MySQL, runs 5 real ML evaluations
│   ├── requirements.txt                # Python backend dependencies
│   └── .env.example                    # Sample database connection environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/                 # Reusable UI elements
│   │   ├── layouts/
│   │   │   └── AppLayout.jsx           # Enterprise layout with sidebar, header, status pills
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx       # Executive KPIs, Recharts trends, recent runs table
│   │   │   ├── DatasetsPage.jsx        # Dataset catalog, search, CSV upload modal
│   │   │   ├── DatasetVersionsPage.jsx # Version lineage, column profiling, 10-row preview
│   │   │   ├── DataQualityPage.jsx     # Quality monitoring, check runner, deterministic scores
│   │   │   ├── ModelsPage.jsx          # AI Model registry, register model modal
│   │   │   ├── ModelVersionsPage.jsx   # Algorithmic version history, add version modal
│   │   │   ├── EvaluationsPage.jsx     # Evaluation engine, launch modal, confusion matrix
│   │   │   ├── ComparisonPage.jsx      # Side-by-side run comparison of 2-4 evaluations
│   │   │   ├── DriftPage.jsx           # Population Stability Index breakdown table
│   │   │   ├── ReliabilityPage.jsx     # Signature formula breakdown, component scores
│   │   │   └── AboutPage.jsx           # Academic details, interactive 12-entity ER mapping
│   │   ├── services/
│   │   │   └── api.js                  # Centralized fetch API client with error handling
│   │   ├── App.jsx                     # State-based tab router
│   │   ├── main.jsx                    # React DOM entry point
│   │   └── index.css                   # Tailwind directives and custom scrollbar styling
│   ├── package.json                    # Node dependencies (React, Vite, Recharts, Lucide)
│   ├── tailwind.config.js              # Tailwind theme extensions
│   ├── postcss.config.js               # PostCSS Autoprefixer config
│   └── vite.config.js                  # Vite bundler configuration with /api proxy
│
├── database/
│   ├── schema.sql                      # DDL creating all 12 tables, constraints, and indexes
│   ├── seed.sql                        # SQL dump of reproducible baseline demo records
│   ├── views.sql                       # 4 analytical views for aggregated reporting
│   └── useful_queries.sql              # 17 advanced DBMS queries (Joins, GROUP BY, Window Funcs)
│
├── storage/
│   ├── datasets/                       # Uploaded and versioned CSV files (safe from traversal)
│   ├── models/                         # Serialized Scikit-learn pipelines (.joblib)
│   └── reports/                        # Detailed JSON audit reports and downloadable summaries
│
├── docs/                               # 10 comprehensive technical documentation files
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   ├── ER_DIAGRAM.md
│   ├── API_DOCUMENTATION.md
│   ├── ML_METHODOLOGY.md
│   ├── RELIABILITY_FORMULA.md
│   ├── SETUP_GUIDE.md
│   ├── VIVA_PREPARATION.md
│   └── LEARNING_ROADMAP.md
│
├── .gitignore                          # Clean repository exclusions
└── README.md                           # Professional GitHub presentation overview
```

---

## 12-Phase Study Plan

### Phase 1: Project Architecture and Folder Structure
- **Objective:** Understand how the modular monolith separates concerns across `database/`, `backend/`, `frontend/`, `storage/`, and `docs/`.
- **Files to Study:** `docs/ARCHITECTURE.md`, `backend/app/main.py`.
- **Exercise:** Trace the complete journey of a request from the frontend button to the database and back.

### Phase 2: MySQL & Relational Database Design
- **Objective:** Master all 12 entities, constraints, foreign keys, and indexes.
- **Files to Study:** `database/schema.sql`, `docs/DATABASE_DESIGN.md`, `docs/ER_DIAGRAM.md`.
- **Exercise:** Run `SHOW CREATE TABLE evaluation_run;` in MySQL Workbench and inspect the foreign key definitions.

### Phase 3: SQLAlchemy & Database Integration
- **Objective:** Learn how SQLAlchemy ORM maps Python classes to MySQL tables without raw SQL strings.
- **Files to Study:** `backend/app/database.py`, `backend/app/models/`.
- **Concepts:** Session lifecycle, connection pooling (`pool_pre_ping`), transactional rollbacks.

### Phase 4: FastAPI & REST APIs
- **Objective:** Understand route definitions, dependency injection (`Depends(get_db)`), and Pydantic schemas.
- **Files to Study:** `backend/app/routers/`, `backend/app/schemas/`.
- **Exercise:** Open `http://localhost:8000/docs` and test calling `/api/users` and `/api/datasets` directly from Swagger UI.

### Phase 5: React Frontend & Recharts
- **Objective:** Understand component modularity, state management (`useState`, `useEffect`), and Recharts visualization.
- **Files to Study:** `frontend/src/App.jsx`, `frontend/src/layouts/AppLayout.jsx`, `frontend/src/pages/DashboardPage.jsx`.
- **Exercise:** Open the browser developer console on `http://localhost:5173` and inspect the JSON payload received from `/api/dashboard/overview`.

### Phase 6: CSV Processing with Pandas
- **Objective:** Learn how Pandas profiles raw files, extracts column types, counts missing cells, and detects duplicates.
- **Files to Study:** `backend/app/services/dataset_service.py`.
- **Key Function:** `DatasetService.profile_csv(path)`.

### Phase 7: Data Quality Algorithms
- **Objective:** Learn how deterministic scoring algorithms evaluate missingness, uniqueness, types, and ranges.
- **Files to Study:** `backend/app/services/quality_service.py`, `backend/tests/test_quality.py`.
- **Key Function:** `QualityService._evaluate_check(df, check_type)`.

### Phase 8: Machine Learning Models & Evaluation
- **Objective:** Understand leak-free Scikit-learn pipelines, column transformers, stratified splitting, and Joblib serialization.
- **Files to Study:** `backend/app/services/evaluation_service.py`, `docs/ML_METHODOLOGY.md`.
- **Key Function:** `EvaluationService.run_evaluation(db, req)`.

### Phase 9: Drift Detection (Population Stability Index)
- **Objective:** Master quantile binning, the mathematical PSI formula, and Kolmogorov-Smirnov CDF testing.
- **Files to Study:** `backend/app/services/drift_service.py`, `backend/tests/test_drift.py`.
- **Key Function:** `DriftService.calculate_psi(expected, actual)`.

### Phase 10: Reliability Scoring Engine
- **Objective:** Understand the 3-pillar weighted formula ($0.35 \text{ DQ} + 0.45 \text{ Model} + 0.20 \text{ Drift}$) and diagnostic reasoning.
- **Files to Study:** `backend/app/services/reliability_service.py`, `docs/RELIABILITY_FORMULA.md`.
- **Key Function:** `ReliabilityService.calculate_reliability(db, eval_id)`.

### Phase 11: Testing & Debugging
- **Objective:** Learn how to write unit and integration tests using Pytest and Starlette TestClient.
- **Files to Study:** `backend/tests/`.
- **Exercise:** Run `python -m pytest -v` in the terminal and inspect the execution time and assertions.

### Phase 12: GitHub Showcase & Interview Preparation
- **Objective:** Be prepared to answer any technical or conceptual question during placement interviews.
- **Files to Study:** `docs/VIVA_PREPARATION.md`, `README.md`.
- **Exercise:** Review the 42 questions in `docs/VIVA_PREPARATION.md` until you can explain the architecture fluidly without referring to notes.
