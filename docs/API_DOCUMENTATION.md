# REST API Reference & Endpoint Specification

## 1. Overview & Base URL

The backend exposes a structured RESTful API implemented in FastAPI.
- **Base URL:** `http://localhost:8000/api`
- **Swagger Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc Alternative:** `http://localhost:8000/redoc`

---

## 2. API Endpoints by Domain

### 2.1 System & Health
- `GET /health`: Returns service name, database name, and status (`{"status": "healthy"}`).

### 2.2 Dashboard Analytics
- `GET /api/dashboard/overview`: Returns KPI counts, averages, trend lines (accuracy, quality, drift), and reliability rating distributions.

### 2.3 Users (`user`)
- `GET /api/users`: List registered users (`skip`, `limit`).
- `POST /api/users`: Create user (`name`, `email`, `role`, `department`).
- `GET /api/users/{id}`: Retrieve single user profile.

### 2.4 Data Sources (`data_source`)
- `GET /api/data-sources`: List registered upstream data sources.
- `POST /api/data-sources`: Create data source (`source_name`, `source_type`, `location`).

### 2.5 Datasets & Versions (`dataset`, `dataset_version`)
- `GET /api/datasets`: List datasets with version counts and latest version numbers.
- `POST /api/datasets`: Create dataset metadata.
- `POST /api/datasets/upload`: Upload new CSV dataset via `multipart/form-data`. Automatically creates dataset, saves CSV safely, profiles columns with Pandas, creates Version 1.0, and executes baseline data quality checks.
- `POST /api/datasets/{id}/upload-version`: Upload new CSV version snapshot for an existing dataset (e.g. v2.0).
- `GET /api/datasets/{id}`: Detailed dataset profile with all version records.
- `PUT /api/datasets/{id}`: Update dataset metadata.
- `DELETE /api/datasets/{id}`: Delete a dataset and its versions, quality checks/results, evaluation history, CSV snapshots, and evaluation reports.
- `GET /api/datasets/{id}/versions`: List version history for a dataset.
- `GET /api/dataset-versions/{id}`: Inspect specific version with column profile (numerical vs categorical), record counts, quality summary, and 10-row CSV preview.

### 2.6 Data Quality (`data_quality_check`, `data_quality_result`)
- `GET /api/quality-checks`: List defined quality checks (optional `?dataset_id={id}`).
- `POST /api/quality-checks`: Define new custom quality check rule (`dataset_id`, `check_name`, `check_type`, `threshold`).
- `POST /api/dataset-versions/{id}/run-quality-checks`: Execute data quality checks on actual CSV file. Computes scores ($0–100$) and assigns status (`PASSED`, `WARNING`, `FAILED`).
- `GET /api/dataset-versions/{id}/quality-results`: Retrieve check results for a specific dataset version.
- `GET /api/quality-results`: List all historical quality results.

### 2.7 AI Models (`ai_model`, `model_version`)
- `GET /api/models`: List registered AI models.
- `POST /api/models`: Register model (`model_name`, `model_type`, `description`, `owner_id`).
- `GET /api/models/{id}`: Detailed model profile with versions.
- `PUT /api/models/{id}`: Update model metadata.
- `POST /api/models/{id}/versions`: Register algorithmic version (`version_number`, `algorithm`).
- `GET /api/models/{id}/versions`: List versions for a model.
- `GET /api/model-versions/{id}`: Inspect version details and evaluation statistics.

### 2.8 Model Evaluations (`evaluation_run`, `evaluation_result`)
- `POST /api/evaluations`: Launch model evaluation pipeline.
  ```json
  {
    "model_version_id": 2,
    "dataset_version_id": 2,
    "executed_by": 1,
    "target_column": "is_fraud",
    "test_size": 0.20,
    "random_state": 42
  }
  ```
  Trains model with Scikit-learn, serializes artifact (.joblib), records metrics, triggers drift detection, calculates reliability, and returns full execution result.
- `GET /api/evaluations`: List runs with optional filtering (`model_id`, `dataset_id`, `status_filter`).
- `GET /api/evaluations/{id}`: Full audit report including confusion matrix, classification report, and drift breakdown.
- `GET /api/evaluations/{id}/results`: Raw metrics (accuracy, precision, recall, F1).
- `GET /api/evaluations/compare?ids=1&ids=2`: Side-by-side comparison across multiple evaluation runs.

### 2.9 Drift Monitoring (`drift_detection`)
- `GET /api/drift`: List all drift records.
- `GET /api/evaluations/{id}/drift`: Retrieve feature-level PSI breakdown and Kolmogorov-Smirnov $p$-values.

### 2.10 Reliability Engine (`reliability_score`)
- `GET /api/reliability`: List all composite reliability scores.
- `GET /api/evaluations/{id}/reliability`: Retrieve component breakdown, weights, diagnostic reasons, and recommendations.
- `GET /api/reliability/formula`: Retrieve platform formula documentation.

### 2.11 Audit Reports
- `GET /api/reports/evaluations/{id}`: Retrieve full report JSON.
- `GET /api/reports/evaluations/{id}/download?format=csv`: Download formatted tabular CSV summary report.
