# Comprehensive Viva Voce & Technical Interview Guide (42 Q&As)

This document prepares you to explain the **AI Model Evaluation & Data Reliability Platform** with high technical confidence during academic viva examinations, placement interviews, and GitHub portfolio reviews.

---

## Part 1: DBMS Fundamentals, Normalization & ER Modeling

### Q1: What is the main objective of this DBMS project?
**Answer:** The objective is to design and implement a normalized relational database (12 core entities) in MySQL that acts as a single source of truth for tracking machine learning models, dataset snapshots, automated data quality results, statistical drift measurements, and an overall composite reliability score.

### Q2: Why is a relational database preferred over a NoSQL document database for this system?
**Answer:** Relational databases provide strict ACID compliance and enforce referential integrity. In model evaluation and governance, strict relational constraints (e.g. guaranteeing an evaluation run links to a valid model version and dataset snapshot, and that quality checks belong to the same logical dataset) prevent corrupted audit trails. Additionally, complex multi-table SQL joins and aggregations are essential for calculating leaderboard rankings and historical trend metrics.

### Q3: What is the difference between a Primary Key and a Unique Key? Where are they used in your schema?
**Answer:** 
- A **Primary Key** uniquely identifies each row in a table and cannot contain `NULL` values. In our schema, every table uses a surrogate integer primary key (e.g., `dataset_id`, `model_version_id`, `evaluation_id`).
- A **Unique Key** prevents duplicate values in a column or set of columns but may permit `NULL` (depending on DBMS). In our schema:
  - `user.email` is UNIQUE to prevent duplicate user accounts.
  - `(dataset_id, version_number)` in `dataset_version` is a composite UNIQUE constraint ensuring a dataset cannot have two identical version tags.
  - `evaluation_result.evaluation_id` and `reliability_score.evaluation_id` have UNIQUE constraints to enforce a 1:1 relationship with `evaluation_run`.

### Q4: Explain the difference between 1:1, 1:N, and M:N relationships in your database.
**Answer:**
- **1:1 (One-to-One):** `evaluation_run` &rarr; `evaluation_result`. Each evaluation produces exactly one consolidated performance result, enforced by `UNIQUE(evaluation_id)` on the child table.
- **1:N (One-to-Many):** `dataset` &rarr; `dataset_version`. One dataset can have multiple immutable version snapshots over time.
- **M:N (Many-to-Many):** Modeled through `evaluation_run`. A model version can evaluate multiple dataset versions, and a dataset version can be evaluated by multiple model versions. `evaluation_run` acts as the associative entity holding metadata like `execution_date` and `status`.

### Q5: What is Database Normalization? To what normal form is your database normalized?
**Answer:** Normalization is the systematic process of organizing database attributes to reduce data redundancy and eliminate update, insertion, and deletion anomalies. Our database is normalized to **Third Normal Form (3NF)**:
1. **1NF:** All attribute values are atomic; no repeating arrays or comma-delimited fields.
2. **2NF:** It is in 1NF, and all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies on composite keys).
3. **3NF:** It is in 2NF, and there are no transitive dependencies ($X \rightarrow Y \rightarrow Z$). Non-key attributes depend only on the primary key.

### Q6: What are Referential Integrity Constraints? What ON DELETE and ON UPDATE actions did you use?
**Answer:** Referential integrity ensures that foreign key relationships remain valid:
- `ON DELETE CASCADE`: Used for child version and result records. If a `dataset` is deleted, its `dataset_version`, `data_quality_check`, and `data_quality_result` rows are automatically deleted to avoid orphaned records.
- `ON DELETE RESTRICT`: Used for entity ownership (`user` and `data_source`). A user or data source cannot be deleted if active datasets or AI models reference them.
- `ON UPDATE CASCADE`: If an identifier is updated, all foreign key references cascade automatically.

### Q7: What are CHECK constraints and how are they used in your database?
**Answer:** A `CHECK` constraint limits the range of values that can be inserted into a column. In our schema:
- `data_quality_result.score`: `CHECK (score >= 0 AND score <= 100)`
- `data_quality_result.status`: `CHECK (status IN ('PASSED', 'FAILED', 'WARNING'))`
- `evaluation_run.status`: `CHECK (status IN ('COMPLETED', 'RUNNING', 'FAILED'))`
- `drift_detection.drift_status`: `CHECK (drift_status IN ('LOW', 'MEDIUM', 'HIGH'))`
- `reliability_score.rating`: `CHECK (rating IN ('LOW', 'MEDIUM', 'HIGH'))`

### Q8: What is a B-Tree Database Index? Why did you add indexes on foreign keys?
**Answer:** A B-Tree index is a balanced search-tree data structure that allows the MySQL storage engine (InnoDB) to locate rows in $O(\log N)$ time rather than performing full table scans in $O(N)$. We created indexes on all foreign key columns (e.g. `idx_evaluation_model`, `idx_evaluation_dataset`) to accelerate join operations between evaluation runs, model versions, and dataset versions.

### Q9: What is an SQL View? What views did you create and why?
**Answer:** An SQL View is a virtual table defined by a saved query. It simplifies complex queries, encapsulates multi-table joins, and enhances performance. We created 4 views:
1. `view_evaluation_overview`: Joins 7 tables to provide a complete picture of an evaluation run with model, dataset, results, drift, and reliability.
2. `view_dataset_quality_summary`: Aggregates check results to display average quality score, pass count, and fail count per dataset version.
3. `view_model_leaderboard`: Computes model version performance metrics and average reliability scores.
4. `view_drift_alerts`: Filters evaluations with `MEDIUM` or `HIGH` drift flags for monitoring.

### Q10: What are ACID properties and how do they apply to this platform?
**Answer:**
- **Atomicity:** All operations in an evaluation transaction (saving results, recording drift, saving reliability) either complete fully or roll back completely.
- **Consistency:** Database state transitions only in ways that satisfy all constraints (primary keys, foreign keys, checks).
- **Isolation:** Multiple concurrent evaluations executing at the same time cannot see uncommitted partial states of each other.
- **Durability:** Once an evaluation is committed, its records persist in MySQL transaction logs even in the event of a system power failure.

---

## Part 2: SQL Queries, Joins & Aggregations

### Q11: What is the difference between an INNER JOIN and a LEFT JOIN?
**Answer:** 
- `INNER JOIN` returns only rows that have matching values in both tables. We use it when linking `evaluation_run` to `model_version` and `dataset_version` because an evaluation cannot exist without both.
- `LEFT JOIN` returns all rows from the left table and matched rows from the right table (filling with `NULL` where no match exists). We use it when querying evaluation runs with optional drift or reliability records, ensuring runs that failed before drift calculation are still returned.

### Q12: How does the GROUP BY clause work with aggregate functions?
**Answer:** `GROUP BY` collapses rows with identical values in specified columns into summary rows. Aggregate functions (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`) compute values across each group. For example, in `view_dataset_quality_summary`, we group by `dataset_version_id` to compute `AVG(score)` and `COUNT(quality_result_id)`.

### Q13: What is the difference between WHERE and HAVING?
**Answer:** 
- `WHERE` filters individual rows **before** aggregation occurs.
- `HAVING` filters aggregated groups **after** `GROUP BY` is applied. For example: `HAVING COUNT(er.evaluation_id) >= 2` filters only models that have been evaluated multiple times.

### Q14: What is a Correlated Subquery? Where is it used in your SQL queries?
**Answer:** A correlated subquery is an inner query that references a column from the outer query for each row processed. In `useful_queries.sql` (Query 12), we use a correlated subquery to find the most recent evaluation date for every individual model:
```sql
WHERE er.execution_date = (
    SELECT MAX(er_inner.execution_date)
    FROM evaluation_run er_inner
    JOIN model_version mv_inner ON er_inner.model_version_id = mv_inner.model_version_id
    WHERE mv_inner.model_id = m.model_id
);
```

### Q15: What is a Window Function in SQL?
**Answer:** A window function performs a calculation across a set of table rows that are related to the current row, without collapsing them into a single row like `GROUP BY`. In Query 17, we use `DENSE_RANK() OVER (ORDER BY avg_f1 DESC)` to rank models by their average F1-score without losing row granularity.

---

## Part 3: Backend, REST APIs & System Integration

### Q16: Why did you choose FastAPI over Flask or Django?
**Answer:** FastAPI offers native asynchronous (`async/await`) request processing, built-in input validation via Pydantic v2, high execution performance on Uvicorn, and automatic generation of interactive OpenAPI/Swagger documentation (`/docs`), which simplifies API testing and frontend integration.

### Q17: What is SQLAlchemy and how does it prevent SQL injection?
**Answer:** SQLAlchemy is a Python Object Relational Mapper (ORM) and SQL toolkit. It prevents SQL injection attacks by strictly using **parameterized queries**—user inputs are transmitted as bound parameter values rather than concatenated directly into SQL text, ensuring input characters like quotes cannot alter query semantics.

### Q18: What is Pydantic and how is it used in your backend?
**Answer:** Pydantic is a data validation library that uses Python type hints. In our backend, Pydantic schemas validate incoming request payloads (e.g. `EvaluationRunCreate`), reject invalid values with HTTP 422, serialize SQLAlchemy ORM models into clean JSON responses (`from_attributes=True`), and prevent internal database passwords or private columns from being exposed to clients.

### Q19: What HTTP status codes are used across your REST API?
**Answer:**
- `200 OK`: Successful resource retrieval (`GET`) or execution.
- `201 Created`: Successful entity creation (`POST` for dataset, user, model).
- `204 No Content`: Successful deletion without response body (`DELETE`).
- `400 Bad Request`: Validation failure (e.g. non-CSV file extension, duplicate version number).
- `404 Not Found`: Requested ID does not exist in the database.
- `413 Payload Too Large`: Uploaded CSV exceeds 50 MB safety threshold.
- `422 Unprocessable Entity`: Pydantic schema validation error.
- `500 Internal Server Error`: Server-side unhandled exception.

### Q20: How are uploaded CSV files stored securely without path traversal vulnerabilities?
**Answer:**
1. Files are stored in an isolated filesystem directory (`storage/datasets/`) completely outside the public web root.
2. Filenames are deterministically generated on the server (`dataset_{id}_v{version}.csv`) using regex sanitization (`[^a-zA-Z0-9_\-\.]`).
3. Path containment verification (`target_path.resolve().is_relative_to(...)`) guarantees that malicious filenames (e.g. `../../etc/passwd`) are rejected with an HTTP 400 error.

---

## Part 4: Machine Learning & Preprocessing Methodology

### Q21: What is Data Leakage and how did you prevent it?
**Answer:** Data leakage occurs when information from outside the training dataset (such as test set statistics) is inadvertently used to train the model. We prevent data leakage using Scikit-learn's `Pipeline` combined with `ColumnTransformer`. The dataset is split **first** into train and test sets using `train_test_split`. Preprocessing transformers (imputation medians and scaling means) are fitted **strictly on the training split** and then applied to transform the holdout test split.

### Q22: Why is SimpleImputer with median preferred over mean for numerical features?
**Answer:** The mean is sensitive to extreme outliers, whereas the median represents the 50th percentile and is resilient to skewness. In financial datasets (e.g. bank transaction amounts), a few multi-million-dollar transactions would artificially inflate the mean, corrupting imputed values.

### Q23: Why do we use OneHotEncoder with `handle_unknown='ignore'`?
**Answer:** OneHotEncoder converts discrete string categories into numerical indicator columns. In production, incoming data versions may introduce previously unseen categories. With `handle_unknown='ignore'`, unseen categories are encoded as all zeros rather than raising a runtime exception that would crash the evaluation pipeline.

### Q24: What is Stratified Splitting and why is it essential for classification?
**Answer:** Stratified splitting (`stratify=y`) ensures that the train and test subsets contain approximately the same percentage of samples of each target class as the complete dataset. For imbalanced problems like fraud detection (e.g. 5% fraud, 95% non-fraud), random splitting could result in a test set with almost zero fraud cases.

### Q25: Why is Accuracy alone insufficient to measure model performance?
**Answer:** On imbalanced datasets, a naive dummy model that always predicts the majority class will achieve high accuracy while providing zero real-world utility. For example, if 98% of transactions are legitimate, predicting legitimate every time yields 98% accuracy but 0% recall on fraud. Precision, recall, and F1-score are necessary to measure true performance.

### Q26: Explain the trade-off between Precision and Recall.
**Answer:**
- **High Precision, Low Recall:** The model is conservative; when it flags fraud, it is almost certainly right, but it misses many actual frauds.
- **High Recall, Low Precision:** The model catches almost all frauds, but triggers many false alarms on innocent customers.
- **F1-score:** The harmonic mean balancing both extremes.

### Q27: How does a Random Forest Classifier work?
**Answer:** Random Forest is an ensemble of $B$ decision trees trained on bootstrap samples of the training data (Bagging). At each node split, a random subset of features is evaluated rather than all features. This decorrelates individual trees, reducing variance and preventing overfitting. The final prediction is determined by majority vote across all trees.

### Q28: How are trained machine learning models persisted?
**Answer:** Fitted Scikit-learn pipelines are serialized to disk using `joblib.dump(pipeline, filename)` in `storage/models/model_version_{id}.joblib`. Joblib is optimized for Python objects containing large NumPy arrays.

---

## Part 5: Data Drift & Statistical Methodology

### Q29: What is Data Drift (Covariate Shift)?
**Answer:** Data drift occurs when the joint distribution of input features $P(\mathbf{X})$ changes over time between the historical reference training distribution and the current production inference distribution, even if the conditional relationship $P(y|\mathbf{X})$ remains intact.

### Q30: What is the Population Stability Index (PSI) and how is it calculated?
**Answer:** PSI is a metric measuring how much a variable has shifted between a reference baseline distribution and a current distribution:
$$PSI = \sum_{b=1}^B (Actual_b\% - Expected_b\%) \times \ln\left(\frac{Actual_b\%}{Expected_b\%}\right)$$
The reference dataset is segmented into 10 quantile bins ($B=10$), and the proportion of records falling into each bin is compared against the actual dataset. Laplace smoothing ($\epsilon = 10^{-4}$) is applied to avoid $\ln(0)$ or division by zero.

### Q31: What are the standard PSI threshold benchmarks?
**Answer:**
- $\text{PSI} < 0.10$: **LOW Drift** &rarr; Minimal change; population is stable.
- $0.10 \le \text{PSI} \le 0.25$: **MEDIUM Drift** &rarr; Moderate shift; active monitoring recommended.
- $\text{PSI} > 0.25$: **HIGH Drift** &rarr; Significant distribution shift; model retraining is required.

### Q32: What is the Kolmogorov-Smirnov (KS) 2-sample test?
**Answer:** The two-sample KS test is a non-parametric statistical hypothesis test that compares the continuous cumulative distribution functions (CDFs) of two samples:
$$D = \sup_x |F_{\text{reference}}(x) - F_{\text{current}}(x)|$$
A small $p$-value ($p < 0.05$) rejects the null hypothesis that both samples come from the same distribution, confirming statistically significant drift.

### Q33: How does your platform handle drift when evaluating the very first version of a dataset?
**Answer:** For Version 1.0 of a dataset, there is no historical predecessor. The platform records a baseline drift score of `0.0000` with status `LOW` and clearly documents in the audit report that this version serves as the initial statistical baseline, rather than fabricating a simulated drift result.

---

## Part 6: Reliability Scoring & Explainability

### Q34: What is the platform's signature reliability formula?
**Answer:**
$$\text{Overall Reliability} = (0.35 \times S_{\text{DQ}}) + (0.45 \times S_{\text{Model}}) + (0.20 \times S_{\text{Drift}})$$
- $S_{\text{DQ}}$: Average data quality check score ($0–100$).
- $S_{\text{Model}}$: Balanced model metric: $(0.40 \times \text{Accuracy}) + (0.60 \times \text{F1-score})$.
- $S_{\text{Drift}}$: Inverted drift health: $\max(0, \min(100, 100 - (\text{PSI} \times 200)))$.

### Q35: Why does Model Performance receive the highest weight (45%)?
**Answer:** The primary functional mission of an AI deployment is making correct inferences. While data hygiene and drift stability are critical prerequisites, a model that cannot achieve high accuracy and F1 score is functionally useless even if data is 100% clean.

### Q36: Why must higher drift severity reduce the Drift Health Score?
**Answer:** PSI is an error metric (higher means more drift). To combine it into a positive reliability index where 100 is best, drift must be inverted: when PSI reaches $0.25$ (the high drift threshold), Drift Health drops to $50.00$; when PSI reaches $0.50$, Drift Health drops to $0.00$.

### Q37: What happens to the reliability rating if data drift is high but accuracy is still high?
**Answer:** The overall score drops into the `MEDIUM` or `LOW` tier because the drift health component contributes a low score. The platform flags this condition in its diagnostic recommendations: "High data drift detected; while current test accuracy appears satisfactory, incoming population no longer matches training assumptions—schedule immediate retraining."

---

## Part 7: Data Quality Monitoring

### Q38: What data quality checks are implemented in your platform?
**Answer:** Six deterministic checks:
1. `missing_values`: Percentage of non-null cells across the dataset.
2. `duplicates`: Percentage of unique rows across the dataset.
3. `data_types`: Validating that numerical features contain parseable floats/integers without string contamination.
4. `numerical_range`: Outlier detection using the Interquartile Range ($3 \times \text{IQR}$).
5. `categorical_validity`: Verifying that categorical values do not contain placeholder tokens like `'?'`, `'N/A'`, or whitespace.
6. `schema_integrity`: Verifying non-empty rows, no entirely null columns, and no unnamed index columns.

### Q39: How are quality check status badges determined?
**Answer:**
- $\text{Score} \ge \text{Threshold}$: **PASSED**
- $\text{Score} \ge (\text{Threshold} - 15.0)$: **WARNING**
- $\text{Score} < (\text{Threshold} - 15.0)$: **FAILED**

---

## Part 8: Frontend Architecture & Enterprise Design

### Q40: What libraries are used in your React frontend and why?
**Answer:**
- **React 18 & Vite:** Fast component rendering with instantaneous Hot Module Replacement.
- **Tailwind CSS:** Modern utility-first styling delivering consistent typography, subtle borders, and an enterprise SaaS aesthetic.
- **Recharts:** Composable charting library rendering responsive Area, Line, Bar, and Pie charts directly from API payloads.
- **Lucide React:** Consistent iconography for data entities, metrics, and navigation.

### Q41: How does the frontend handle API errors or an offline database?
**Answer:** The frontend features a global health poller probing `/health` every 30 seconds to display connection status in the sidebar. API requests are wrapped in centralized try/catch blocks that surface descriptive error banners and retry buttons rather than blank screens.

### Q42: How does the Model Comparison feature work?
**Answer:** The user selects 2 to 4 completed evaluation runs. The frontend queries `/api/evaluations/compare?ids=1&ids=2`, and renders a side-by-side comparison table contrasting algorithm types, dataset snapshots, accuracy, F1-scores, PSI drift, and overall reliability ratings, allowing practitioners to verify whether an algorithm upgrade actually improved reliability.
