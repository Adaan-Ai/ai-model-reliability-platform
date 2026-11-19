# Relational Database Architecture & Schema Specification

## 1. Relational Design Philosophy

In enterprise machine learning systems, data and model metadata are frequently fragmented across disparate files, cloud buckets, and ad-hoc spreadsheets. The **AI Model Evaluation & Data Reliability Platform** enforces the relational database as the **single source of truth**.

The database architecture is designed in **Third Normal Form (3NF)** and strictly implements the 12 core entities approved in the DBMS design submission (`279_307.pdf`).

---

## 2. Comprehensive Entity Analysis

### Entity 1: `user`
- **Purpose:** Represents data scientists, ML engineers, data platform managers, and compliance auditors who own assets or trigger evaluations.
- **Attributes:**
  - `user_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `name` (`VARCHAR(100)`, `NOT NULL`)
  - `email` (`VARCHAR(150)`, `NOT NULL`, `UNIQUE`)
  - `role` (`VARCHAR(50)`, `NOT NULL`)
  - `department` (`VARCHAR(100)`, `NOT NULL`)
- **Relationships:**
  - One `user` can own multiple `dataset` records (1:N).
  - One `user` can own multiple `ai_model` records (1:N).
  - One `user` can execute multiple `evaluation_run` records (1:N).
- **Real-World Example:** `Mohammed Adaan Hamad`, `Lead Engineer`, `Data Science`.

---

### Entity 2: `data_source`
- **Purpose:** Models the upstream origin or data ingestion source supplying datasets.
- **Attributes:**
  - `source_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `source_name` (`VARCHAR(150)`, `NOT NULL`)
  - `source_type` (`VARCHAR(50)`, `NOT NULL`)
  - `location` (`VARCHAR(255)`, `NULL`)
- **Relationships:**
  - One `data_source` can supply multiple `dataset` records (1:N).
- **Real-World Example:** `Core Banking Transaction Lake`, `S3 Data Lake`, `s3://pesu-banking-data/transactions/`.

---

### Entity 3: `dataset`
- **Purpose:** Represents a logical business dataset domain (e.g. Fraud Detection stream, Subscriber Churn).
- **Attributes:**
  - `dataset_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `dataset_name` (`VARCHAR(150)`, `NOT NULL`)
  - `description` (`TEXT`, `NULL`)
  - `source_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `data_source.source_id`)
  - `owner_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `user.user_id`)
  - `created_date` (`DATE`, `NOT NULL`)
- **Relationships:**
  - Belongs to one `data_source` (N:1).
  - Owned by one `user` (N:1).
  - Can have multiple immutable `dataset_version` records (1:N).
  - Can have multiple defined `data_quality_check` rules (1:N).
- **Referential Integrity:** `ON DELETE RESTRICT ON UPDATE CASCADE` for owner and source.

---

### Entity 4: `dataset_version`
- **Purpose:** Tracks immutable snapshots of the dataset over time as incoming records grow or change.
- **Attributes:**
  - `dataset_version_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `dataset_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `dataset.dataset_id`)
  - `version_number` (`VARCHAR(30)`, `NOT NULL`)
  - `record_count` (`BIGINT`, `NOT NULL`)
  - `created_date` (`DATE`, `NOT NULL`)
- **Constraints:** `UNIQUE(dataset_id, version_number)` prevents duplicate version labels under the same dataset.
- **Relationships:**
  - Belongs to one logical `dataset` (N:1).
  - Can have multiple `data_quality_result` evaluations (1:N).
  - Can participate in multiple `evaluation_run` experiments (1:N).
- **Referential Integrity:** `ON DELETE CASCADE ON UPDATE CASCADE`.

---

### Entity 5: `data_quality_check`
- **Purpose:** Defines a reusable data quality rule and validation threshold configured for a dataset.
- **Attributes:**
  - `quality_check_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `dataset_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `dataset.dataset_id`)
  - `check_name` (`VARCHAR(150)`, `NOT NULL`)
  - `check_type` (`VARCHAR(50)`, `NOT NULL`)
  - `threshold` (`DECIMAL(5,2)`, `NULL`)
- **Supported Check Types:** `missing_values`, `duplicates`, `data_types`, `numerical_range`, `categorical_validity`, `schema_integrity`.
- **Relationships:**
  - Belongs to one `dataset` (N:1).
  - Can generate multiple historical `data_quality_result` records (1:N).

---

### Entity 6: `data_quality_result`
- **Purpose:** Stores the actual execution score and verification status of a check against a specific dataset version snapshot.
- **Attributes:**
  - `quality_result_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `quality_check_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `data_quality_check.quality_check_id`)
  - `dataset_version_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `dataset_version.dataset_version_id`)
  - `score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(score >= 0 AND score <= 100)`)
  - `status` (`VARCHAR(20)`, `NOT NULL`, `CHECK(status IN ('PASSED','FAILED','WARNING'))`)
  - `execution_date` (`DATETIME`, `NOT NULL`)
- **Logical Validation:** Application enforces that `quality_check.dataset_id == dataset_version.dataset_id`.

---

### Entity 7: `ai_model`
- **Purpose:** Logical registry for artificial intelligence / machine learning models.
- **Attributes:**
  - `model_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `model_name` (`VARCHAR(150)`, `NOT NULL`)
  - `model_type` (`VARCHAR(80)`, `NOT NULL`)
  - `description` (`TEXT`, `NULL`)
  - `owner_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `user.user_id`)
  - `created_date` (`DATE`, `NOT NULL`)
- **Relationships:**
  - Owned by one `user` (N:1).
  - Has multiple `model_version` iterations (1:N).

---

### Entity 8: `model_version`
- **Purpose:** Tracks specific algorithmic iterations and hyperparameter variants for a model.
- **Attributes:**
  - `model_version_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `model_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `ai_model.model_id`)
  - `version_number` (`VARCHAR(30)`, `NOT NULL`)
  - `algorithm` (`VARCHAR(100)`, `NOT NULL`)
  - `created_date` (`DATE`, `NOT NULL`)
- **Constraints:** `UNIQUE(model_id, version_number)`.
- **Supported Algorithms:** `Logistic Regression`, `Random Forest`, `Decision Tree`.
- **Relationships:**
  - Belongs to one `ai_model` (N:1).
  - Participates in multiple `evaluation_run` records (1:N).

---

### Entity 9: `evaluation_run` (Central Hub Entity)
- **Purpose:** The central operational entity recording the execution of an evaluation experiment.
- **Attributes:**
  - `evaluation_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `model_version_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `model_version.model_version_id`)
  - `dataset_version_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `dataset_version.dataset_version_id`)
  - `executed_by` (`INT`, `NOT NULL`, Foreign Key &rarr; `user.user_id`)
  - `execution_date` (`DATETIME`, `NOT NULL`)
  - `status` (`VARCHAR(20)`, `NOT NULL`, `CHECK(status IN ('COMPLETED','RUNNING','FAILED'))`)
- **Relationships:**
  - Many-to-one with `model_version`, `dataset_version`, and `user`.
  - Produces exactly one `evaluation_result` (1:1).
  - Produces one or more `drift_detection` measurements (1:N).
  - Receives exactly one `reliability_score` (1:1).

---

### Entity 10: `evaluation_result`
- **Purpose:** Stores the consolidated classification performance metrics for a completed evaluation run.
- **Attributes:**
  - `result_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `evaluation_id` (`INT`, `NOT NULL`, `UNIQUE`, Foreign Key &rarr; `evaluation_run.evaluation_id`)
  - `accuracy` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `precision_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `recall_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `f1_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
- **Cardinality:** 1:1 with `evaluation_run` via `UNIQUE(evaluation_id)`.

---

### Entity 11: `drift_detection`
- **Purpose:** Stores statistical distribution shift measurements comparing the evaluated dataset with earlier reference baselines.
- **Attributes:**
  - `drift_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `evaluation_id` (`INT`, `NOT NULL`, Foreign Key &rarr; `evaluation_run.evaluation_id`)
  - `drift_score` (`DECIMAL(6,4)`, `NOT NULL`, `CHECK(drift_score >= 0)`)
  - `drift_status` (`VARCHAR(20)`, `NOT NULL`, `CHECK(drift_status IN ('LOW','MEDIUM','HIGH'))`)
  - `detected_date` (`DATETIME`, `NOT NULL`)
- **Cardinality:** 1:N with `evaluation_run`.

---

### Entity 12: `reliability_score`
- **Purpose:** Stores the holistic composite reliability index combining data quality, model metrics, and drift.
- **Attributes:**
  - `reliability_id` (`INT`, Primary Key, `AUTO_INCREMENT`)
  - `evaluation_id` (`INT`, `NOT NULL`, `UNIQUE`, Foreign Key &rarr; `evaluation_run.evaluation_id`)
  - `data_quality_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `model_performance_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `drift_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `overall_score` (`DECIMAL(5,2)`, `NOT NULL`, `CHECK(0..100)`)
  - `rating` (`VARCHAR(20)`, `NOT NULL`, `CHECK(rating IN ('LOW','MEDIUM','HIGH'))`)
- **Cardinality:** 1:1 with `evaluation_run` via `UNIQUE(evaluation_id)`.

---

## 3. Normalization Analysis

### First Normal Form (1NF)
- All attribute values are atomic (scalar numbers, strings, dates, datetimes).
- No repeating groups or comma-separated lists stored in columns.
- Every table has a clearly designated Primary Key.

### Second Normal Form (2NF)
- The database is in 1NF.
- All non-key attributes are fully functionally dependent on the entire primary key. In all entities, the primary key is a single surrogate key (`INT AUTO_INCREMENT`), which inherently prevents partial key dependencies.

### Third Normal Form (3NF)
- The database is in 2NF.
- There are no transitive dependencies ($X \rightarrow Y$ and $Y \rightarrow Z$ where $X$ is primary key). For instance, owner details (`name`, `department`) are not stored in `dataset`; instead, `owner_id` references `user`. Similarly, algorithm details are separated into `model_version` rather than redundant in `evaluation_run`.

---

## 4. Performance Indexes

The schema includes explicit B-Tree indexes matching the submission DDL to ensure high-performance joins and filter operations:
- `idx_dataset_source ON dataset(source_id)`
- `idx_dataset_owner ON dataset(owner_id)`
- `idx_dataset_version_dataset ON dataset_version(dataset_id)`
- `idx_quality_result_version ON data_quality_result(dataset_version_id)`
- `idx_model_owner ON ai_model(owner_id)`
- `idx_model_version_model ON model_version(model_id)`
- `idx_evaluation_model ON evaluation_run(model_version_id)`
- `idx_evaluation_dataset ON evaluation_run(dataset_version_id)`
- `idx_evaluation_date ON evaluation_run(execution_date)`
- `idx_drift_evaluation ON drift_detection(evaluation_id)`
