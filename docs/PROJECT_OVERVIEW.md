# AI Model Evaluation & Data Reliability Platform — Project Overview

## 1. Executive Summary

Organizations increasingly depend on machine learning and artificial intelligence systems to automate high-stakes decisions: fraud detection, credit risk scoring, customer churn prediction, medical diagnosis, and financial forecasting. 

However, **a machine learning model is only as reliable as the data that powers it**. When models fail in real-world deployments, the root cause is rarely the mathematical algorithm itself—it is usually:
1. **Silent Data Quality Decay:** Missing values, schema mutations, duplicate transactions, and out-of-range sensor readings entering the inference pipeline undetected.
2. **Covariate Shift / Data Drift:** The statistical distribution of incoming production data diverging from historical training data over time due to economic shifts, seasonal trends, or changing user behavior.
3. **Lack of Lineage & Reproducibility:** Teams losing track of which model version was trained on which dataset snapshot, under what hyperparameters, and with what historical benchmark results.
4. **Decoupled Evaluation:** Model performance metrics (accuracy, F1) being evaluated in isolation from data quality metrics and drift measurements, leading to false confidence.

The **AI Model Evaluation & Data Reliability Platform** solves these challenges by combining a normalized **12-entity relational database in MySQL** with a **Python/FastAPI analytics engine** and an **enterprise React analytics interface**.

---

## 2. Project Authors & Academic Context

- **Institution:** PES University, Department of Computer Science & Engineering
- **Project Domain:** Database Management Systems (DBMS) Laboratory Project
- **Lead Developer:** Mohammed Adaan Hamad (`PES2UG24CS279`)
- **Co-Developer:** Navya Kishore Dash (`PES2UG24CS307`)
- **Authoritative Foundation:** Project submission document `279_307.pdf`

---

## 3. Core System Objectives

1. **Centralized Relational Lineage:** Maintain the database as the authoritative source of truth tracking datasets, versions, models, algorithmic versions, evaluation runs, and audit outcomes.
2. **Automated Data Quality Verification:** Execute deterministic validation checks (missing values, uniqueness, data types, numerical ranges, categorical validity, schema integrity) against raw CSV datasets.
3. **Leak-Free Machine Learning Pipeline:** Train and evaluate supervised classification models (Logistic Regression, Random Forest, Decision Tree) with stratified splits and strict column preprocessing pipelines.
4. **Explainable Drift Monitoring:** Implement Population Stability Index (PSI) and Kolmogorov-Smirnov statistical tests to calculate exact distribution shifts across numerical and categorical features.
5. **Holistic Reliability Indexing:** Unify data quality, model performance, and drift health into a single weighted reliability score:
   $$\text{Overall Reliability} = (0.35 \times \text{Data Quality}) + (0.45 \times \text{Model Performance}) + (0.20 \times \text{Drift Health})$$
6. **Auditability & Exportability:** Provide downloadable CSV and JSON audit reports for compliance, governance, and model risk management.

---

## 4. Key Differentiators vs Basic CRUD Projects

| Capability | Basic University Project | AI Model Evaluation & Data Reliability Platform |
|---|---|---|
| **Database Design** | 3–4 disconnected tables | **12 normalized entities** with referential integrity, check constraints, cascade rules, and analytical views |
| **Data Quality** | Manual checks or dummy flags | **6 automated deterministic algorithms** profiling raw CSV files with Pandas |
| **Model Evaluation** | Hardcoded accuracy or dummy numbers | **Real Scikit-learn pipelines** executing stratified splits, confusion matrices, and Joblib serialization |
| **Drift Detection** | None or simulated random text | **Real Population Stability Index (PSI) & KS 2-sample tests** comparing distributions across version snapshots |
| **Reliability Score** | Simple average of accuracy | **Weighted multi-pillar index** balancing data hygiene, predictive power, and population stability |
| **User Interface** | Basic Bootstrap / HTML forms | **Modern enterprise SaaS interface** with Recharts analytics, drag-and-drop CSV uploads, and comparison matrices |
