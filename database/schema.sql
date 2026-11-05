-- ==============================================================================
-- AI Model Evaluation & Data Reliability Platform
-- Database Definition (DDL) Schema
-- DBMS Project - Mohammed Adaan Hamad (PES2UG24CS279) & Navya Kishore Dash (PES2UG24CS307)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS ai_model_reliability;
USE ai_model_reliability;

-- 1. USER
CREATE TABLE IF NOT EXISTS user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL
);

-- 2. DATA_SOURCE
CREATE TABLE IF NOT EXISTS data_source (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    source_name VARCHAR(150) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    location VARCHAR(255)
);

-- 3. DATASET
CREATE TABLE IF NOT EXISTS dataset (
    dataset_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_name VARCHAR(150) NOT NULL,
    description TEXT,
    source_id INT NOT NULL,
    owner_id INT NOT NULL,
    created_date DATE NOT NULL,
    FOREIGN KEY (source_id) REFERENCES data_source(source_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES user(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 4. DATASET_VERSION
CREATE TABLE IF NOT EXISTS dataset_version (
    dataset_version_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    version_number VARCHAR(30) NOT NULL,
    record_count BIGINT NOT NULL,
    created_date DATE NOT NULL,
    UNIQUE (dataset_id, version_number),
    FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 5. DATA_QUALITY_CHECK
CREATE TABLE IF NOT EXISTS data_quality_check (
    quality_check_id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    check_name VARCHAR(150) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    threshold DECIMAL(5,2),
    FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6. DATA_QUALITY_RESULT
CREATE TABLE IF NOT EXISTS data_quality_result (
    quality_result_id INT PRIMARY KEY AUTO_INCREMENT,
    quality_check_id INT NOT NULL,
    dataset_version_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    execution_date DATETIME NOT NULL,
    CHECK (score >= 0 AND score <= 100),
    CHECK (status IN ('PASSED','FAILED','WARNING')),
    FOREIGN KEY (quality_check_id) REFERENCES data_quality_check(quality_check_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (dataset_version_id) REFERENCES dataset_version(dataset_version_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 7. AI_MODEL
CREATE TABLE IF NOT EXISTS ai_model (
    model_id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(150) NOT NULL,
    model_type VARCHAR(80) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_date DATE NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES user(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 8. MODEL_VERSION
CREATE TABLE IF NOT EXISTS model_version (
    model_version_id INT PRIMARY KEY AUTO_INCREMENT,
    model_id INT NOT NULL,
    version_number VARCHAR(30) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    created_date DATE NOT NULL,
    UNIQUE (model_id, version_number),
    FOREIGN KEY (model_id) REFERENCES ai_model(model_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 9. EVALUATION_RUN
CREATE TABLE IF NOT EXISTS evaluation_run (
    evaluation_id INT PRIMARY KEY AUTO_INCREMENT,
    model_version_id INT NOT NULL,
    dataset_version_id INT NOT NULL,
    executed_by INT NOT NULL,
    execution_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    CHECK (status IN ('COMPLETED','RUNNING','FAILED')),
    FOREIGN KEY (model_version_id) REFERENCES model_version(model_version_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (dataset_version_id) REFERENCES dataset_version(dataset_version_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (executed_by) REFERENCES user(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 10. EVALUATION_RESULT
CREATE TABLE IF NOT EXISTS evaluation_result (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    evaluation_id INT NOT NULL UNIQUE,
    accuracy DECIMAL(5,2) NOT NULL,
    precision_score DECIMAL(5,2) NOT NULL,
    recall_score DECIMAL(5,2) NOT NULL,
    f1_score DECIMAL(5,2) NOT NULL,
    CHECK (accuracy BETWEEN 0 AND 100),
    CHECK (precision_score BETWEEN 0 AND 100),
    CHECK (recall_score BETWEEN 0 AND 100),
    CHECK (f1_score BETWEEN 0 AND 100),
    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 11. DRIFT_DETECTION
CREATE TABLE IF NOT EXISTS drift_detection (
    drift_id INT PRIMARY KEY AUTO_INCREMENT,
    evaluation_id INT NOT NULL,
    drift_score DECIMAL(6,4) NOT NULL,
    drift_status VARCHAR(20) NOT NULL,
    detected_date DATETIME NOT NULL,
    CHECK (drift_score >= 0),
    CHECK (drift_status IN ('LOW','MEDIUM','HIGH')),
    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 12. RELIABILITY_SCORE
CREATE TABLE IF NOT EXISTS reliability_score (
    reliability_id INT PRIMARY KEY AUTO_INCREMENT,
    evaluation_id INT NOT NULL UNIQUE,
    data_quality_score DECIMAL(5,2) NOT NULL,
    model_performance_score DECIMAL(5,2) NOT NULL,
    drift_score DECIMAL(5,2) NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    rating VARCHAR(20) NOT NULL,
    CHECK (data_quality_score BETWEEN 0 AND 100),
    CHECK (model_performance_score BETWEEN 0 AND 100),
    CHECK (drift_score BETWEEN 0 AND 100),
    CHECK (overall_score BETWEEN 0 AND 100),
    CHECK (rating IN ('LOW','MEDIUM','HIGH')),
    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Submission Document Indexes
CREATE INDEX idx_dataset_source ON dataset(source_id);
CREATE INDEX idx_dataset_owner ON dataset(owner_id);
CREATE INDEX idx_dataset_version_dataset ON dataset_version(dataset_id);
CREATE INDEX idx_quality_result_version ON data_quality_result(dataset_version_id);
CREATE INDEX idx_model_owner ON ai_model(owner_id);
CREATE INDEX idx_model_version_model ON model_version(model_id);
CREATE INDEX idx_evaluation_model ON evaluation_run(model_version_id);
CREATE INDEX idx_evaluation_dataset ON evaluation_run(dataset_version_id);
CREATE INDEX idx_evaluation_date ON evaluation_run(execution_date);
CREATE INDEX idx_drift_evaluation ON drift_detection(evaluation_id);
