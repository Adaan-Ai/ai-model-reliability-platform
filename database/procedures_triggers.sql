-- ==============================================================================
-- AI Model Evaluation & Data Reliability Platform
-- Stored Procedures, Functions, and Triggers (DBMS Lab Requirement)
-- ==============================================================================

USE ai_model_reliability;

DROP PROCEDURE IF EXISTS sp_calculate_composite_reliability;
DROP PROCEDURE IF EXISTS sp_generate_model_evaluation_summary;
DROP FUNCTION IF EXISTS fn_get_reliability_rating;
DROP TRIGGER IF EXISTS trg_validate_quality_result_dataset;
DROP TRIGGER IF EXISTS trg_prevent_completed_evaluation_deletion;
DROP TRIGGER IF EXISTS trg_auto_update_evaluation_status;

DELIMITER $$

-- ------------------------------------------------------------------------------
-- 1. STORED FUNCTION: fn_get_reliability_rating
-- Calculates rating tier ('HIGH', 'MEDIUM', 'LOW') from numeric overall score
-- ------------------------------------------------------------------------------
CREATE FUNCTION fn_get_reliability_rating(p_score DECIMAL(5,2))
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE v_rating VARCHAR(20);
    IF p_score >= 80.0 THEN
        SET v_rating = 'HIGH';
    ELSEIF p_score >= 65.0 THEN
        SET v_rating = 'MEDIUM';
    ELSE
        SET v_rating = 'LOW';
    END IF;
    RETURN v_rating;
END$$

-- ------------------------------------------------------------------------------
-- 2. STORED PROCEDURE: sp_calculate_composite_reliability
-- Computes the weighted reliability score for an evaluation run:
-- Overall = 0.35 * DataQuality + 0.45 * ModelPerformance + 0.20 * DriftHealth
-- ------------------------------------------------------------------------------
CREATE PROCEDURE sp_calculate_composite_reliability(
    IN p_evaluation_id INT
)
BEGIN
    DECLARE v_dataset_version_id INT;
    DECLARE v_dq_score DECIMAL(5,2) DEFAULT 85.00;
    DECLARE v_accuracy DECIMAL(5,2);
    DECLARE v_precision DECIMAL(5,2);
    DECLARE v_recall DECIMAL(5,2);
    DECLARE v_f1 DECIMAL(5,2);
    DECLARE v_model_score DECIMAL(5,2) DEFAULT 0.00;
    DECLARE v_drift_score DECIMAL(6,4);
    DECLARE v_drift_health DECIMAL(5,2) DEFAULT 100.00;
    DECLARE v_overall_score DECIMAL(5,2) DEFAULT 0.00;
    DECLARE v_rating VARCHAR(20);

    -- 1. Retrieve dataset_version_id for the given evaluation run
    SELECT dataset_version_id INTO v_dataset_version_id
    FROM evaluation_run
    WHERE evaluation_id = p_evaluation_id;

    -- 2. Calculate average data quality score from data_quality_result
    SELECT COALESCE(AVG(score), 85.00) INTO v_dq_score
    FROM data_quality_result
    WHERE dataset_version_id = v_dataset_version_id;

    -- 3. Retrieve model performance metrics from evaluation_result
    SELECT accuracy, precision_score, recall_score, f1_score
    INTO v_accuracy, v_precision, v_recall, v_f1
    FROM evaluation_result
    WHERE evaluation_id = p_evaluation_id;

    IF v_accuracy IS NOT NULL THEN
        SET v_model_score = (0.40 * v_f1) + (0.30 * v_accuracy) + (0.15 * v_precision) + (0.15 * v_recall);
    ELSE
        SET v_model_score = 75.00;
    END IF;

    -- 4. Retrieve drift score from drift_detection
    SELECT drift_score INTO v_drift_score
    FROM drift_detection
    WHERE evaluation_id = p_evaluation_id
    ORDER BY detected_date DESC
    LIMIT 1;

    IF v_drift_score IS NOT NULL THEN
        -- Drift penalty: health drops from 100 down as PSI increases
        SET v_drift_health = GREATEST(0.00, 100.00 - (v_drift_score * 200.0));
    ELSE
        SET v_drift_health = 100.00;
    END IF;

    -- 5. Calculate composite overall score: 35% DQ + 45% Model + 20% Drift
    SET v_overall_score = (0.35 * v_dq_score) + (0.45 * v_model_score) + (0.20 * v_drift_health);
    SET v_rating = fn_get_reliability_rating(v_overall_score);

    -- 6. Insert or update reliability_score record
    INSERT INTO reliability_score (
        evaluation_id, data_quality_score, model_performance_score, drift_score, overall_score, rating
    ) VALUES (
        p_evaluation_id, v_dq_score, v_model_score, v_drift_health, v_overall_score, v_rating
    ) ON DUPLICATE KEY UPDATE
        data_quality_score = VALUES(data_quality_score),
        model_performance_score = VALUES(model_performance_score),
        drift_score = VALUES(drift_score),
        overall_score = VALUES(overall_score),
        rating = VALUES(rating);

    -- Return the calculated row
    SELECT * FROM reliability_score WHERE evaluation_id = p_evaluation_id;
END$$

-- ------------------------------------------------------------------------------
-- 3. STORED PROCEDURE: sp_generate_model_evaluation_summary
-- Summarizes all evaluation runs, average accuracy, F1, and reliability for an AI model
-- ------------------------------------------------------------------------------
CREATE PROCEDURE sp_generate_model_evaluation_summary(
    IN p_model_id INT
)
BEGIN
    SELECT 
        m.model_id,
        m.model_name,
        mv.version_number,
        mv.algorithm,
        COUNT(er.evaluation_id) AS total_evaluations,
        ROUND(AVG(res.accuracy), 2) AS avg_accuracy,
        ROUND(AVG(res.f1_score), 2) AS avg_f1_score,
        ROUND(AVG(rs.overall_score), 2) AS avg_reliability,
        MAX(er.execution_date) AS last_evaluated
    FROM ai_model m
    JOIN model_version mv ON m.model_id = mv.model_id
    LEFT JOIN evaluation_run er ON mv.model_version_id = er.model_version_id
    LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id
    LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id
    WHERE m.model_id = p_model_id
    GROUP BY m.model_id, m.model_name, mv.version_number, mv.algorithm;
END$$

-- ------------------------------------------------------------------------------
-- 4. TRIGGER: trg_validate_quality_result_dataset
-- Validates that quality_check and dataset_version belong to the same logical dataset
-- Prevents inconsistent foreign key combinations (Enforces Section 3.6 of specs)
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_validate_quality_result_dataset
BEFORE INSERT ON data_quality_result
FOR EACH ROW
BEGIN
    DECLARE v_check_dataset_id INT;
    DECLARE v_version_dataset_id INT;

    SELECT dataset_id INTO v_check_dataset_id
    FROM data_quality_check
    WHERE quality_check_id = NEW.quality_check_id;

    SELECT dataset_id INTO v_version_dataset_id
    FROM dataset_version
    WHERE dataset_version_id = NEW.dataset_version_id;

    IF v_check_dataset_id != v_version_dataset_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: Quality check and Dataset Version do not belong to the same Dataset!';
    END IF;
END$$

-- ------------------------------------------------------------------------------
-- 5. TRIGGER: trg_prevent_completed_evaluation_deletion
-- Ensures that an evaluation run marked 'COMPLETED' cannot be deleted (Audit Trail)
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_prevent_completed_evaluation_deletion
BEFORE DELETE ON evaluation_run
FOR EACH ROW
BEGIN
    IF OLD.status = 'COMPLETED' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Audit Violation: Completed evaluation runs cannot be deleted from the system!';
    END IF;
END$$

-- ------------------------------------------------------------------------------
-- 6. TRIGGER: trg_auto_update_evaluation_status
-- Automatically marks evaluation_run status as 'COMPLETED' when results are saved
-- ------------------------------------------------------------------------------
CREATE TRIGGER trg_auto_update_evaluation_status
AFTER INSERT ON evaluation_result
FOR EACH ROW
BEGIN
    UPDATE evaluation_run
    SET status = 'COMPLETED'
    WHERE evaluation_id = NEW.evaluation_id;
END$$

DELIMITER ;
