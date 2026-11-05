-- ==============================================================================
-- AI Model Evaluation & Data Reliability Platform
-- Database Analytical Views
-- DBMS Project - Mohammed Adaan Hamad & Navya Kishore Dash
-- ==============================================================================

USE ai_model_reliability;

-- View 1: Complete Evaluation Overview with Model, Dataset, Result, Drift, and Reliability
CREATE OR REPLACE VIEW view_evaluation_overview AS
SELECT 
    er.evaluation_id,
    er.execution_date,
    er.status AS run_status,
    u.name AS executed_by_name,
    m.model_id,
    m.model_name,
    m.model_type,
    mv.model_version_id,
    mv.version_number AS model_version,
    mv.algorithm,
    d.dataset_id,
    d.dataset_name,
    dv.dataset_version_id,
    dv.version_number AS dataset_version,
    dv.record_count,
    res.accuracy,
    res.precision_score,
    res.recall_score,
    res.f1_score,
    dd.drift_score,
    dd.drift_status,
    rs.data_quality_score,
    rs.model_performance_score,
    rs.drift_score AS reliability_drift_score,
    rs.overall_score AS reliability_overall_score,
    rs.rating AS reliability_rating
FROM evaluation_run er
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
JOIN user u ON er.executed_by = u.user_id
LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
LEFT JOIN drift_detection dd ON er.evaluation_id = dd.evaluation_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id;

-- View 2: Dataset Version Quality Summary
CREATE OR REPLACE VIEW view_dataset_quality_summary AS
SELECT 
    d.dataset_id,
    d.dataset_name,
    dv.dataset_version_id,
    dv.version_number,
    dv.record_count,
    COUNT(dqr.quality_result_id) AS total_checks_executed,
    ROUND(AVG(dqr.score), 2) AS average_quality_score,
    SUM(CASE WHEN dqr.status = 'PASSED' THEN 1 ELSE 0 END) AS passed_checks,
    SUM(CASE WHEN dqr.status = 'WARNING' THEN 1 ELSE 0 END) AS warning_checks,
    SUM(CASE WHEN dqr.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_checks,
    MAX(dqr.execution_date) AS latest_check_date
FROM dataset_version dv
JOIN dataset d ON dv.dataset_id = d.dataset_id
LEFT JOIN data_quality_result dqr ON dv.dataset_version_id = dqr.dataset_version_id
GROUP BY d.dataset_id, d.dataset_name, dv.dataset_version_id, dv.version_number, dv.record_count;

-- View 3: Model Performance & Reliability Leaderboard
CREATE OR REPLACE VIEW view_model_leaderboard AS
SELECT 
    m.model_id,
    m.model_name,
    m.model_type,
    mv.version_number AS latest_version,
    mv.algorithm,
    COUNT(er.evaluation_id) AS total_evaluations,
    ROUND(AVG(res.accuracy), 2) AS avg_accuracy,
    ROUND(AVG(res.f1_score), 2) AS avg_f1_score,
    ROUND(AVG(rs.overall_score), 2) AS avg_reliability_score,
    MAX(er.execution_date) AS last_evaluated_at
FROM ai_model m
JOIN model_version mv ON m.model_id = mv.model_id
LEFT JOIN evaluation_run er ON mv.model_version_id = er.model_version_id AND er.status = 'COMPLETED'
LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
GROUP BY m.model_id, m.model_name, m.model_type, mv.version_number, mv.algorithm;

-- View 4: Drift Alert Monitoring
CREATE OR REPLACE VIEW view_drift_alerts AS
SELECT 
    dd.drift_id,
    dd.evaluation_id,
    dd.drift_score,
    dd.drift_status,
    dd.detected_date,
    m.model_name,
    mv.version_number AS model_version,
    d.dataset_name,
    dv.version_number AS dataset_version,
    rs.overall_score AS reliability_score,
    rs.rating AS reliability_rating
FROM drift_detection dd
JOIN evaluation_run er ON dd.evaluation_id = er.evaluation_id
JOIN model_version mv ON er.model_version_id = mv.model_version_id
JOIN ai_model m ON mv.model_id = m.model_id
JOIN dataset_version dv ON er.dataset_version_id = dv.dataset_version_id
JOIN dataset d ON dv.dataset_id = d.dataset_id
LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
WHERE dd.drift_status IN ('MEDIUM', 'HIGH');
