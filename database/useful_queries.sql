-- ==============================================================================
-- AI Model Evaluation & Data Reliability Platform
-- Analytical & Operational SQL Queries (DBMS Submission Requirement)
-- Covers: Joins, Aggregations, GROUP BY, HAVING, Correlated Subqueries, Window Functions
-- ==============================================================================

USE ai_model_reliability;

-- ------------------------------------------------------------------------------
-- Query 1: List all datasets with their owners and data source locations
-- Demonstrates: Multi-table INNER JOIN with column aliasing
-- ------------------------------------------------------------------------------
SELECT 
    d.dataset_id,
    d.dataset_name,
    d.description,
    ds.source_name,
    ds.source_type,
    ds.location AS storage_location,
    u.name AS owner_name,
    u.email AS owner_email,
    u.department,
    d.created_date
FROM dataset d
JOIN data_source ds ON d.source_id = ds.source_id
JOIN user u ON d.owner_id = u.user_id
ORDER BY d.created_date DESC;

-- ------------------------------------------------------------------------------
-- Query 2: List dataset versions with parent dataset name and cumulative metrics
-- Demonstrates: Parent-child JOIN with version ordering
-- ------------------------------------------------------------------------------
SELECT 
    dv.dataset_version_id,
    d.dataset_name,
    dv.version_number,
    dv.record_count,
    dv.created_date
FROM dataset_version dv
JOIN dataset d ON dv.dataset_id = d.dataset_id
ORDER BY d.dataset_name ASC, dv.created_date DESC;

-- ------------------------------------------------------------------------------
-- Query 3: Find AI models owned by a particular user or department
-- Demonstrates: Filtering by foreign key and department with model count
-- ------------------------------------------------------------------------------
SELECT 
    m.model_id,
    m.model_name,
    m.model_type,
    m.description,
    u.name AS owner_name,
    u.department,
    m.created_date
FROM ai_model m
JOIN user u ON m.owner_id = u.user_id
WHERE u.department = 'Data Science' OR u.name LIKE '%Adaan%'
ORDER BY m.model_name;

-- ------------------------------------------------------------------------------
-- Query 4: Find all evaluations for a specific model with full lineage
-- Demonstrates: Joining evaluation_run with model_version, dataset_version, and results
-- ------------------------------------------------------------------------------
SELECT 
    er.evaluation_id,
    m.model_name,
    mv.version_number AS model_version,
    mv.algorithm,
    d.dataset_name,
    dv.version_number AS dataset_version,
    er.execution_date,
    er.status,
    res.accuracy,
    res.f1_score,
    rs.overall_score AS reliability_score
FROM evaluation_run er
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
WHERE m.model_id = 1
ORDER BY er.execution_date DESC;

-- ------------------------------------------------------------------------------
-- Query 5: Compare model performance across algorithm types and versions
-- Demonstrates: GROUP BY with aggregate functions (AVG, MIN, MAX)
-- ------------------------------------------------------------------------------
SELECT 
    m.model_name,
    mv.version_number,
    mv.algorithm,
    COUNT(er.evaluation_id) AS total_runs,
    ROUND(AVG(res.accuracy), 2) AS avg_accuracy,
    ROUND(AVG(res.precision_score), 2) AS avg_precision,
    ROUND(AVG(res.recall_score), 2) AS avg_recall,
    ROUND(AVG(res.f1_score), 2) AS avg_f1_score
FROM model_version mv
JOIN ai_model m ON mv.model_id = m.model_id
JOIN evaluation_run er ON mv.model_version_id = er.model_version_id
JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
WHERE er.status = 'COMPLETED'
GROUP BY m.model_name, mv.version_number, mv.algorithm
ORDER BY avg_f1_score DESC;

-- ------------------------------------------------------------------------------
-- Query 6: Find datasets with failed data quality checks
-- Demonstrates: Filtering by result status with threshold comparison
-- ------------------------------------------------------------------------------
SELECT 
    d.dataset_name,
    dv.version_number,
    dqc.check_name,
    dqc.check_type,
    dqc.threshold,
    dqr.score AS actual_score,
    dqr.status,
    dqr.execution_date
FROM data_quality_result dqr
JOIN data_quality_check dqc ON dqr.quality_check_id = dqc.quality_check_id
JOIN dataset_version dv ON dqr.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
WHERE dqr.status = 'FAILED'
ORDER BY dqr.execution_date DESC;

-- ------------------------------------------------------------------------------
-- Query 7: Find evaluations with HIGH drift detection
-- Demonstrates: Filtering drift measurements exceeding critical thresholds
-- ------------------------------------------------------------------------------
SELECT 
    dd.drift_id,
    er.evaluation_id,
    m.model_name,
    mv.version_number AS model_version,
    d.dataset_name,
    dv.version_number AS dataset_version,
    dd.drift_score,
    dd.drift_status,
    dd.detected_date
FROM drift_detection dd
JOIN evaluation_run er ON dd.evaluation_id = er.evaluation_id
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
WHERE dd.drift_status = 'HIGH'
ORDER BY dd.drift_score DESC;

-- ------------------------------------------------------------------------------
-- Query 8: Find evaluations with LOW reliability rating
-- Demonstrates: Filtering joined reliability records and inspecting component deficits
-- ------------------------------------------------------------------------------
SELECT 
    rs.reliability_id,
    er.evaluation_id,
    m.model_name,
    mv.version_number AS model_version,
    d.dataset_name,
    dv.version_number AS dataset_version,
    rs.data_quality_score,
    rs.model_performance_score,
    rs.drift_score,
    rs.overall_score,
    rs.rating
FROM reliability_score rs
JOIN evaluation_run er ON rs.evaluation_id = er.evaluation_id
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
WHERE rs.rating = 'LOW'
ORDER BY rs.overall_score ASC;

-- ------------------------------------------------------------------------------
-- Query 9: Calculate overall average model accuracy and standard metrics
-- Demonstrates: Scalar aggregation across all completed evaluations
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS completed_evaluations,
    ROUND(AVG(accuracy), 2) AS overall_avg_accuracy,
    ROUND(AVG(precision_score), 2) AS overall_avg_precision,
    ROUND(AVG(recall_score), 2) AS overall_avg_recall,
    ROUND(AVG(f1_score), 2) AS overall_avg_f1
FROM evaluation_result res
JOIN evaluation_run er ON res.evaluation_id = er.evaluation_id
WHERE er.status = 'COMPLETED';

-- ------------------------------------------------------------------------------
-- Query 10: Calculate average reliability score grouped by AI model
-- Demonstrates: GROUP BY with HAVING clause to filter models evaluated multiple times
-- ------------------------------------------------------------------------------
SELECT 
    m.model_id,
    m.model_name,
    m.model_type,
    COUNT(er.evaluation_id) AS evaluation_count,
    ROUND(AVG(rs.data_quality_score), 2) AS avg_dq_score,
    ROUND(AVG(rs.model_performance_score), 2) AS avg_perf_score,
    ROUND(AVG(rs.drift_score), 2) AS avg_drift_score,
    ROUND(AVG(rs.overall_score), 2) AS avg_reliability_score
FROM ai_model m
JOIN model_version mv ON m.model_id = mv.model_id
JOIN evaluation_run er ON mv.model_version_id = er.model_version_id
JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
GROUP BY m.model_id, m.model_name, m.model_type
HAVING COUNT(er.evaluation_id) >= 1
ORDER BY avg_reliability_score DESC;

-- ------------------------------------------------------------------------------
-- Query 11: Identify the most frequently evaluated models
-- Demonstrates: Aggregate COUNT with LIMIT
-- ------------------------------------------------------------------------------
SELECT 
    m.model_name,
    m.model_type,
    COUNT(er.evaluation_id) AS total_evaluations,
    MAX(er.execution_date) AS most_recent_evaluation
FROM ai_model m
JOIN model_version mv ON m.model_id = mv.model_id
JOIN evaluation_run er ON mv.model_version_id = er.model_version_id
GROUP BY m.model_id, m.model_name, m.model_type
ORDER BY total_evaluations DESC
LIMIT 5;

-- ------------------------------------------------------------------------------
-- Query 12: Find the latest evaluation for every registered model
-- Demonstrates: Correlated Subquery
-- ------------------------------------------------------------------------------
SELECT 
    er.evaluation_id,
    m.model_name,
    mv.version_number AS model_version,
    er.execution_date,
    er.status,
    res.accuracy,
    rs.overall_score AS reliability_score,
    rs.rating
FROM evaluation_run er
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
WHERE er.execution_date = (
    SELECT MAX(er_inner.execution_date)
    FROM evaluation_run er_inner
    JOIN model_version mv_inner ON er_inner.model_version_id = mv_inner.model_version_id
    WHERE mv_inner.model_id = m.model_id
);

-- ------------------------------------------------------------------------------
-- Query 13: Identify datasets with the most quality issues (Failed or Warning)
-- Demonstrates: Conditional aggregation and HAVING
-- ------------------------------------------------------------------------------
SELECT 
    d.dataset_id,
    d.dataset_name,
    COUNT(dqr.quality_result_id) AS total_checks,
    SUM(CASE WHEN dqr.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_checks,
    SUM(CASE WHEN dqr.status = 'WARNING' THEN 1 ELSE 0 END) AS warning_checks,
    ROUND(AVG(dqr.score), 2) AS mean_quality_score
FROM dataset d
JOIN dataset_version dv ON d.dataset_id = dv.dataset_id
JOIN data_quality_result dqr ON dv.dataset_version_id = dqr.dataset_version_id
GROUP BY d.dataset_id, d.dataset_name
ORDER BY failed_checks DESC, warning_checks DESC;

-- ------------------------------------------------------------------------------
-- Query 14: Compare reliability scores across versions of the same dataset
-- Demonstrates: Multi-level aggregation tracking version progression
-- ------------------------------------------------------------------------------
SELECT 
    d.dataset_name,
    dv.version_number,
    dv.record_count,
    COUNT(DISTINCT er.evaluation_id) AS evaluations_conducted,
    ROUND(AVG(rs.data_quality_score), 2) AS avg_data_quality,
    ROUND(AVG(rs.drift_score), 2) AS avg_drift_health,
    ROUND(AVG(rs.overall_score), 2) AS avg_overall_reliability
FROM dataset d
JOIN dataset_version dv ON d.dataset_id = dv.dataset_id
LEFT JOIN evaluation_run er ON dv.dataset_version_id = er.dataset_version_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
GROUP BY d.dataset_name, dv.version_number, dv.record_count, dv.created_date
ORDER BY d.dataset_name, dv.created_date ASC;

-- ------------------------------------------------------------------------------
-- Query 15: Comprehensive evaluation summary report
-- Demonstrates: Comprehensive multi-table consolidation with formatted metrics
-- ------------------------------------------------------------------------------
SELECT 
    er.evaluation_id,
    m.model_name,
    mv.version_number AS model_ver,
    d.dataset_name,
    dv.version_number AS data_ver,
    u.name AS executed_by,
    DATE_FORMAT(er.execution_date, '%Y-%m-%d %H:%i') AS run_time,
    CONCAT(res.accuracy, '%') AS accuracy_pct,
    CONCAT(res.f1_score, '%') AS f1_pct,
    dd.drift_status,
    dd.drift_score,
    rs.overall_score AS reliability,
    rs.rating
FROM evaluation_run er
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
JOIN user u ON er.executed_by = u.user_id
LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
LEFT JOIN drift_detection dd ON er.evaluation_id = dd.evaluation_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
ORDER BY er.execution_date DESC;

-- ------------------------------------------------------------------------------
-- Query 16 (Bonus): Data quality check pass rates by check type
-- Demonstrates: GROUP BY on check categorization
-- ------------------------------------------------------------------------------
SELECT 
    dqc.check_type,
    COUNT(dqr.quality_result_id) AS total_runs,
    ROUND(AVG(dqr.score), 2) AS avg_score,
    ROUND(100.0 * SUM(CASE WHEN dqr.status = 'PASSED' THEN 1 ELSE 0 END) / COUNT(dqr.quality_result_id), 2) AS pass_percentage
FROM data_quality_check dqc
JOIN data_quality_result dqr ON dqc.quality_check_id = dqr.quality_check_id
GROUP BY dqc.check_type
ORDER BY pass_percentage DESC;

-- ------------------------------------------------------------------------------
-- Query 17 (Bonus): Top 3 models by average F1 score using Window Function
-- Demonstrates: DENSE_RANK() OVER partition
-- ------------------------------------------------------------------------------
SELECT 
    model_name,
    algorithm,
    avg_f1,
    DENSE_RANK() OVER (ORDER BY avg_f1 DESC) AS performance_rank
FROM (
    SELECT 
        m.model_name,
        mv.algorithm,
        ROUND(AVG(res.f1_score), 2) AS avg_f1
    FROM ai_model m
    JOIN model_version mv ON m.model_id = mv.model_id
    JOIN evaluation_run er ON mv.model_version_id = er.model_version_id
    JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
    WHERE er.status = 'COMPLETED'
    GROUP BY m.model_name, mv.algorithm
) ranked_models;
