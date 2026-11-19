import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

TEMPLATE_PATH = r"C:\Users\Mohammed Adaan\.gemini\antigravity\brain\0737c05c-a196-421e-8e45-ed8092588d0d\.user_uploaded\media_1795064834540_feafcc68.docx"
OUTPUT_PATH = r"C:\Users\Mohammed Adaan\ai-model-reliability-platform\docs\DBMS_Mini_Project_Report_UE23CS351A.docx"

doc = docx.Document(TEMPLATE_PATH)

def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)

def add_para(doc, text="", style='Normal', space_after=6, line_spacing=1.15, bold=False, italic=False, size_pt=12):
    p = doc.add_paragraph(text, style=style)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    for r in p.runs:
        format_run(r, font_name="Times New Roman", size_pt=size_pt, bold=bold, italic=italic)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=16, bold=True)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=13, bold=True)
    return p

def add_code(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_str.strip())
    r.font.name = "Consolas"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0, 0, 0)
    add_para(doc, "", space_after=4)

def add_table_data(doc, col_widths, headers, data):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            format_run(r, font_name="Times New Roman", size_pt=10, bold=True)
    for row_data in data:
        row = tbl.add_row()
        for i, val in enumerate(row_data):
            c = row.cells[i]
            c.text = str(val)
            p = c.paragraphs[0]
            for r in p.runs:
                format_run(r, font_name="Times New Roman", size_pt=10)
    for row in tbl.rows:
        for idx, w in enumerate(col_widths):
            row.cells[idx].width = Inches(w)
    add_para(doc, "", space_after=6)

# -------------------------------------------------------------
# 1. FRONT MATTER MODIFICATIONS
# -------------------------------------------------------------
# Cover Title
p_title = doc.paragraphs[1]
p_title.text = "AI MODEL EVALUATION & DATA RELIABILITY PLATFORM"
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in p_title.runs:
    format_run(r, font_name="Times New Roman", size_pt=16, bold=True)

# Cover Student Table (Table 0)
tbl0 = doc.tables[0]
tbl0.rows[0].cells[0].text = "MOHAMMED ADAAN HAMAD"
tbl0.rows[0].cells[1].text = "PES2UG24CS279"
r2_tbl0 = tbl0.add_row()
r2_tbl0.cells[0].text = "NAVYA KISHORE DASH"
r2_tbl0.cells[1].text = "PES2UG24CS307"
for row in tbl0.rows:
    for c in row.cells:
        for p in c.paragraphs:
            for r in p.runs:
                format_run(r, font_name="Times New Roman", size_pt=11, bold=True)

# Certificate Page (Paragraph 28 & Table 2)
p_cert_title = doc.paragraphs[28]
p_cert_title.text = "AI Model Evaluation & Data Reliability Platform"
p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in p_cert_title.runs:
    format_run(r, font_name="Times New Roman", size_pt=14, bold=True)

tbl2 = doc.tables[2]
tbl2.rows[0].cells[0].text = "MOHAMMED ADAAN HAMAD"
tbl2.rows[0].cells[1].text = "PES2UG24CS279"
r2_tbl2 = tbl2.add_row()
r2_tbl2.cells[0].text = "NAVYA KISHORE DASH"
r2_tbl2.cells[1].text = "PES2UG24CS307"
for row in tbl2.rows:
    for c in row.cells:
        for p in c.paragraphs:
            for r in p.runs:
                format_run(r, font_name="Times New Roman", size_pt=11, bold=True)

tbl3 = doc.tables[3]
tbl3.rows[0].cells[0].text = "___________________________\nDr. Shilpa S\nAssistant Professor & Guide\nDepartment of CSE"
tbl3.rows[0].cells[1].text = "___________________________\nDr. Sandesh B J\nProfessor & Chairperson\nDepartment of CSE"
for c in tbl3.rows[0].cells:
    for p in c.paragraphs:
        for r in p.runs:
            format_run(r, font_name="Times New Roman", size_pt=10, bold=True)

# Declaration Page (Paragraph 43 & Table 4)
p_decl_body = doc.paragraphs[43]
p_decl_body.text = (
    "We hereby declare that the DBMS Project entitled \"AI Model Evaluation & Data Reliability Platform\" "
    "has been carried out by us under the guidance of Dr. Shilpa S, Assistant Professor and submitted in partial fulfilment "
    "of the course requirements for the award of degree of Bachelor of Technology in Computer Science and Engineering of "
    "PES University, Bengaluru during the academic semester AUG – DEC 2026."
)
for r in p_decl_body.runs:
    format_run(r, font_name="Times New Roman", size_pt=12)

tbl4 = doc.tables[4]
tbl4.rows[0].cells[0].text = "MOHAMMED ADAAN HAMAD"
tbl4.rows[0].cells[1].text = "PES2UG24CS279"
tbl4.rows[0].cells[2].text = "<Signature>"
r2_tbl4 = tbl4.add_row()
r2_tbl4.cells[0].text = "NAVYA KISHORE DASH"
r2_tbl4.cells[1].text = "PES2UG24CS307"
r2_tbl4.cells[2].text = "<Signature>"
for row in tbl4.rows:
    for c in row.cells:
        for p in c.paragraphs:
            for r in p.runs:
                format_run(r, font_name="Times New Roman", size_pt=11, bold=True)

# Acknowledgement
p_ack1 = doc.paragraphs[68]
p_ack1.text = (
    "We would like to express our gratitude to Dr. Shilpa S, Department of Computer Science and Engineering, "
    "PES University, for her continuous guidance, assistance, and encouragement throughout the development of this "
    "UE23CS351A - DBMS Project."
)
for r in p_ack1.runs:
    format_run(r, font_name="Times New Roman", size_pt=12)

p_ack2 = doc.paragraphs[69]
p_ack2.text = (
    "We take this opportunity to thank Dr. Sandesh B J, Professor & Chairperson, Department of Computer Science "
    "and Engineering, PES University, for all the knowledge and support we have received from the department."
)
for r in p_ack2.runs:
    format_run(r, font_name="Times New Roman", size_pt=12)

p_ack3 = doc.paragraphs[70]
p_ack3.text = (
    "We are deeply grateful to Prof. Jawahar Doreswamy, Chancellor – PES University, and Dr. Suryaprasad J, "
    "Vice-Chancellor, PES University for providing to us various opportunities and enlightenment every step of the way. "
    "Finally, this DBMS Project could not have been completed without the continual support and encouragement we have "
    "received from our family and friends."
)
for r in p_ack3.runs:
    format_run(r, font_name="Times New Roman", size_pt=12)

# Abstract (Paragraph 85)
p_abs = doc.paragraphs[85]
p_abs.text = (
    "Modern enterprise organizations increasingly depend on Artificial Intelligence (AI) and Machine Learning (ML) "
    "models for critical decision-making, such as credit risk assessment, financial fraud detection, and customer churn "
    "prediction. However, evaluating models solely in static offline environments is insufficient. Production models suffer "
    "from data quality degradation, unmanaged dataset version lineage, and statistical feature drift, leading to silent "
    "catastrophic failures. Without a centralized, normalized database architecture, organizations fail to maintain reproducible "
    "audit trails linking dataset versions, quality metrics, evaluation runs, and drift measurements.\n\n"
    "This project presents the AI Model Evaluation & Data Reliability Platform, an enterprise-grade system designed around "
    "a strict Third Normal Form (3NF) relational database in MySQL. The database architecture is grounded on exactly 12 core "
    "relational entities: USER, DATA_SOURCE, DATASET, DATASET_VERSION, DATA_QUALITY_CHECK, DATA_QUALITY_RESULT, AI_MODEL, "
    "MODEL_VERSION, EVALUATION_RUN, EVALUATION_RESULT, DRIFT_DETECTION, and RELIABILITY_SCORE.\n\n"
    "The system incorporates a robust Python/FastAPI analytics backend integrating leak-free Scikit-learn classification "
    "pipelines, automated Pandas tabular profiling, six deterministic data quality validation algorithms (missingness, "
    "duplicates, data types, numerical range, categorical validity, schema integrity), two-sample Kolmogorov-Smirnov hypothesis "
    "tests, and Population Stability Index (PSI) drift detection. A transparent, mathematically grounded composite reliability "
    "index computes an overall trust score: Overall = (0.35 * DQ) + (0.45 * Model) + (0.20 * Drift). The frontend is engineered "
    "using React 18, Vite, Tailwind CSS, and Recharts, providing real-time confusion matrices, version lineage trees, and "
    "diagnostic recommendations. Stored procedures, functions, and active triggers enforce cross-entity foreign key referential "
    "integrity and audit compliance."
)
for r in p_abs.runs:
    format_run(r, font_name="Times New Roman", size_pt=12)

# Table of Contents (Table 5)
t5 = doc.tables[5]
toc_entries = [
    ("1", "INTRODUCTION", "11"),
    ("2", "PROBLEM DEFINITION", "12"),
    ("3", "ER MODEL", "13"),
    ("4", "ER TO RELATIONAL MAPPING", "14"),
    ("5", "DDL STATEMENTS", "15"),
    ("6", "DML STATEMENTS", "20"),
    ("7", "QUERIES (SIMPLE QUERY, UPDATE, DELETE, CORRELATED, NESTED)", "23"),
    ("8", "STORED PROCEDURES, FUNCTIONS AND TRIGGERS", "30"),
    ("9", "FRONT END DEVELOPMENT", "36"),
    ("", "REFERENCES", "42"),
    ("", "APPENDIX A: DEFINITIONS, ACRONYMS AND ABBREVIATIONS", "43"),
    ("", "GITHUB REPOSITORY LINK", "44")
]
for idx, (c_num, c_title, c_page) in enumerate(toc_entries):
    row_idx = idx + 1
    if row_idx < len(t5.rows):
        r = t5.rows[row_idx]
        r.cells[0].text = c_num
        r.cells[1].text = c_title
        r.cells[2].text = c_page
        for c in r.cells:
            for p in c.paragraphs:
                for run in p.runs:
                    format_run(run, font_name="Times New Roman", size_pt=10)

# List of Tables (Table 6)
t6 = doc.tables[6]
t6_data = [
    ("3.1", "Entity Summary and Descriptions", "13"),
    ("4.1", "Relational Mapping Cardinality Rules", "14"),
    ("5.1", "DDL Table Specifications and Constraints", "15"),
    ("6.1", "Sample Populated Records Summary", "20"),
    ("8.1", "Stored Procedures and Functions Summary", "30"),
    ("8.2", "Active Database Triggers Summary", "33"),
    ("9.1", "Frontend Pages and Functional Capabilities", "38")
]
while len(t6.rows) > 1:
    tr = t6.rows[-1]._tr
    tr.getparent().remove(tr)
for t_num, t_name, t_page in t6_data:
    r = t6.add_row()
    r.cells[0].text = t_num
    r.cells[1].text = t_name
    r.cells[2].text = t_page
    for c in r.cells:
        for p in c.paragraphs:
            for run in p.runs:
                format_run(run, font_name="Times New Roman", size_pt=10)

# List of Figures (Table 7)
t7 = doc.tables[7]
t7_data = [
    ("2.1", "High-Level Architecture of AI Model Evaluation Platform", "12"),
    ("3.1", "Complete Entity-Relationship (ER) Diagram", "13"),
    ("4.1", "Relational Schema Diagram with Foreign Key References", "14"),
    ("7.1", "SQL Query Execution Output", "28"),
    ("8.1", "Trigger Execution Workflow for Referential Integrity", "34"),
    ("9.1", "React Frontend Dashboard Interface", "39"),
    ("9.2", "Confusion Matrix and Model Metrics Visualization", "40"),
    ("9.3", "Population Stability Index Feature Drift Visualization", "41")
]
while len(t7.rows) > 1:
    tr = t7.rows[-1]._tr
    tr.getparent().remove(tr)
for f_num, f_name, f_page in t7_data:
    r = t7.add_row()
    r.cells[0].text = f_num
    r.cells[1].text = f_name
    r.cells[2].text = f_page
    for c in r.cells:
        for p in c.paragraphs:
            for run in p.runs:
                format_run(run, font_name="Times New Roman", size_pt=10)

# -------------------------------------------------------------
# 2. REMOVE PLACEHOLDER PARAGRAPHS FROM NOTE ONWARD
# -------------------------------------------------------------
p183_idx = None
for i, p in enumerate(doc.paragraphs):
    if "NOTE: all the below sections" in p.text:
        p183_idx = i
        break

if p183_idx is not None:
    for p in list(doc.paragraphs)[p183_idx:]:
        p._element.getparent().remove(p._element)

# -------------------------------------------------------------
# 3. APPEND COMPLETE CHAPTERS WITH EXACT TEMPLATE STRUCTURE
# -------------------------------------------------------------

# CHAPTER 1: INTRODUCTION
doc.add_page_break()
add_heading_1(doc, "1. INTRODUCTION")
add_para(doc,
    "In the contemporary software engineering landscape, enterprise organizations are experiencing a fundamental "
    "paradigm shift. Rule-based procedural software systems are rapidly being superseded or augmented by Machine Learning "
    "(ML) and Artificial Intelligence (AI) models. These models drive automated decision-making in high-consequence domains "
    "such as financial transaction fraud detection, customer churn prediction, credit risk underwriting, and autonomous diagnostics. "
    "However, unlike traditional software artifacts where source code remains invariant once compiled, machine learning models "
    "are intrinsically dual-natured: their functional correctness and behavioral reliability depend equally on the serialized "
    "model code/weights and the statistical distributions of the data upon which they operate."
)
add_para(doc,
    "When machine learning models are deployed into production, they do not fail due to conventional syntax or null-pointer errors. "
    "Instead, they suffer from silent degradation. A model that attained 94% accuracy during laboratory training may plummet to 62% "
    "accuracy within weeks due to undetected data corruption, schema mismatches, missing values introduced by upstream ETL pipelines, "
    "or macroeconomic shifts causing covariate and concept drift. In most existing industry setups, data scientists track model "
    "weights in decentralized registries, data engineers maintain datasets in distributed object storage, and quality audits are "
    "conducted through ad-hoc Jupyter notebooks. This architectural fragmentation creates massive operational vulnerabilities:\n"
    "• Evaluations cannot be accurately reproduced because the exact version of the dataset used during an experiment is lost.\n"
    "• There is no relational lineage linking a data quality check result to a specific model version evaluation.\n"
    "• Statistical distribution drift between training baseline data and production inference data is detected post-facto, only after financial loss occurs.\n"
    "• Stakeholders lack a standardized, quantitative, single-pane-of-glass reliability metric that combines data hygiene, predictive prowess, and distributional stability."
)
add_para(doc,
    "The AI Model Evaluation & Data Reliability Platform solves this fundamental engineering challenge. By establishing an authoritative, "
    "Third Normal Form (3NF) relational database in MySQL as the single source of truth, the platform cohesively models the entire "
    "lifecycle of AI reliability. It bridges the gap between Relational Database Management Systems (RDBMS) and modern Machine Learning "
    "Operations (MLOps). The platform tracks users, data sources, datasets, immutable dataset versions, deterministic data quality checks, "
    "AI models, model iterations, evaluation executions, confusion matrix metrics, Population Stability Index (PSI) drift measurements, "
    "and multi-attribute composite reliability scores."
)

# CHAPTER 2: PROBLEM DEFINITION
doc.add_page_break()
add_heading_1(doc, "2. PROBLEM DEFINITION")
add_para(doc,
    "Organizations increasingly rely on AI and machine-learning models for fraud detection, recommendations, forecasting, customer "
    "support, risk analysis, and other business decisions. As these models evolve, organizations need a reliable way to evaluate model "
    "performance, track model and dataset versions, monitor data quality, and detect changes in data that may reduce model reliability. "
    "Without centralized tracking, it becomes difficult to reproduce an evaluation, compare model versions, identify poor-quality data, "
    "or determine whether a model's performance has degraded. The proposed AI Model Evaluation & Data Reliability Platform uses a "
    "relational database to maintain model versions, dataset versions, evaluation runs, data-quality results, drift measurements, "
    "and reliability scores. The platform provides a structured foundation for analyzing whether an AI model and the data supporting "
    "it are reliable enough for continued use."
)
add_heading_2(doc, "Project Objectives")
add_para(doc,
    "1. Relational Database Design: Design a normalized (3NF) schema in MySQL consisting of exactly 12 core entities with strict primary "
    "keys, foreign keys, cascade constraints, check constraints, unique constraints, and B-tree indexes.\n"
    "2. Version Lineage and Integrity: Maintain immutable version tracking for both datasets (tracking record counts, schema changes, "
    "and physical file pointers) and machine learning models (tracking algorithms, hyperparameters, and serialized Joblib artifacts).\n"
    "3. Deterministic Data Quality Engine: Implement automated checks measuring missing values, record duplicates, schema violations, "
    "numerical range compliance, and categorical domain integrity, scoring datasets from 0 to 100.\n"
    "4. Leak-Free Model Evaluation & Statistical Drift Detection: Develop an analytics engine utilizing Scikit-learn classification "
    "pipelines with strict stratified train/test isolation, calculating Accuracy, Precision, Recall, and F1-score, alongside two-sample "
    "Kolmogorov-Smirnov tests and Population Stability Index (PSI) drift tracking.\n"
    "5. Composite Reliability Scoring & Visualization: Synthesize quality, performance, and drift into a single weighted reliability index "
    "and surface the data through an enterprise React/Tailwind/Recharts user interface with full auditability."
)

# CHAPTER 3: ER MODEL
doc.add_page_break()
add_heading_1(doc, "3. ER MODEL")
add_para(doc,
    "The Conceptual Entity-Relationship (ER) model captures the enterprise domain of AI evaluation and data reliability. "
    "The architecture contains 12 entities, mapped strictly to satisfy Third Normal Form (3NF) requirements without data redundancy."
)
ent_data = [
    ("USER", "Platform users, data scientists, and engineers who own assets and execute runs.", "user_id (PK), name, email, role, department"),
    ("DATA_SOURCE", "Identifies the origin of data feeds (e.g., PostgreSQL DB, S3 Bucket, Snowflake).", "source_id (PK), source_name, source_type, location"),
    ("DATASET", "Logical entity grouping multiple versions of a business dataset.", "dataset_id (PK), dataset_name, description, source_id (FK), owner_id (FK), created_date"),
    ("DATASET_VERSION", "Specific immutable release of a dataset with exact record counts and CSV bindings.", "dataset_version_id (PK), dataset_id (FK), version_number, record_count, created_date"),
    ("DATA_QUALITY_CHECK", "Defines deterministic verification rules configured for a logical dataset.", "quality_check_id (PK), dataset_id (FK), check_name, check_type, threshold"),
    ("DATA_QUALITY_RESULT", "The empirical outcome of running a quality check against a dataset version.", "quality_result_id (PK), quality_check_id (FK), dataset_version_id (FK), score, status, execution_date"),
    ("AI_MODEL", "Logical registry for an AI/ML model entity.", "model_id (PK), model_name, model_type, description, owner_id (FK), created_date"),
    ("MODEL_VERSION", "Algorithmic iteration of an AI model with specific architecture and serialized artifact.", "model_version_id (PK), model_id (FK), version_number, algorithm, created_date"),
    ("EVALUATION_RUN", "Central operational entity representing an experimental run binding model and data.", "evaluation_id (PK), model_version_id (FK), dataset_version_id (FK), executed_by (FK), execution_date, status"),
    ("EVALUATION_RESULT", "Performance classification metrics produced by a completed evaluation run (1:1 with run).", "result_id (PK), evaluation_id (FK/Unique), accuracy, precision_score, recall_score, f1_score"),
    ("DRIFT_DETECTION", "Statistical distribution shift measurements comparing baseline and current features.", "drift_id (PK), evaluation_id (FK), drift_score, drift_status, detected_date"),
    ("RELIABILITY_SCORE", "Consolidated composite trust assessment synthesizing quality, performance, and drift (1:1 with run).", "reliability_id (PK), evaluation_id (FK/Unique), data_quality_score, model_performance_score, drift_score, overall_score, rating")
]
add_table_data(doc, [1.5, 3.2, 1.8], ["Entity Name", "Description", "Attributes"], ent_data)

add_heading_2(doc, "Relationship Cardinalities and Constraints")
add_para(doc,
    "1. USER — DATASET (1 : N): One user can create and own multiple datasets; each dataset belongs to exactly one user.\n"
    "2. DATA_SOURCE — DATASET (1 : N): One data source can supply data for multiple datasets; each dataset originates from one source.\n"
    "3. DATASET — DATASET_VERSION (1 : N): One dataset has multiple version iterations (1.0, 2.0); each version references one parent dataset.\n"
    "4. DATASET — DATA_QUALITY_CHECK (1 : N): One dataset defines multiple quality rules; each rule belongs to one dataset.\n"
    "5. DATA_QUALITY_CHECK — DATA_QUALITY_RESULT (1 : N): One check produces multiple results over time as new versions arrive.\n"
    "6. DATASET_VERSION — DATA_QUALITY_RESULT (1 : N): One dataset version is evaluated by multiple quality checks.\n"
    "7. USER — AI_MODEL (1 : N): One user can develop and own multiple AI models.\n"
    "8. AI_MODEL — MODEL_VERSION (1 : N): One AI model tracks multiple algorithmic versions.\n"
    "9. MODEL_VERSION — EVALUATION_RUN (1 : N): One model version can participate in multiple evaluation experiments.\n"
    "10. DATASET_VERSION — EVALUATION_RUN (1 : N): One dataset version can be evaluated against multiple model versions.\n"
    "11. USER — EVALUATION_RUN (1 : N): One user can trigger and execute multiple evaluation runs.\n"
    "12. EVALUATION_RUN — EVALUATION_RESULT (1 : 1): Each completed evaluation run produces exactly one consolidated metrics record.\n"
    "13. EVALUATION_RUN — DRIFT_DETECTION (1 : N): An evaluation run can record multiple feature-level drift scores.\n"
    "14. EVALUATION_RUN — RELIABILITY_SCORE (1 : 1): Each evaluation run receives exactly one composite reliability rating."
)

er_mermaid = (
    "+---------------------------------------------------------------------------------------------------------+\n"
    "|                                     ENTITY RELATIONSHIP DIAGRAM                                         |\n"
    "+---------------------------------------------------------------------------------------------------------+\n"
    "|                                                                                                         |\n"
    "|   [USER] 1 -------< owns >------- N [DATASET] 1 -------< has >------- N [DATASET_VERSION]               |\n"
    "|     |                                  |                                     |                          |\n"
    "|     |                                  | 1                                   | 1                        |\n"
    "|     | owns                             | defines                             | evaluated_in             |\n"
    "|     |                                  v N                                   v N                        |\n"
    "|     |                            [DATA_QUALITY_CHECK] 1 ---> N [DATA_QUALITY_RESULT]                    |\n"
    "|     v N                                                                      |                          |\n"
    "|   [AI_MODEL] 1 ---< has >--- N [MODEL_VERSION] 1                             | used_in                  |\n"
    "|                                       |                                      |                          |\n"
    "|                                       | 1                                    v N                        |\n"
    "|                                       +--------------> [EVALUATION_RUN] <----+                          |\n"
    "|                                                               |                                         |\n"
    "|                            +----------------------------------+----------------------------------+      |\n"
    "|                            | 1                                | 1                                | 1    |\n"
    "|                            v 1                                v N                                v 1    |\n"
    "|                   [EVALUATION_RESULT]                 [DRIFT_DETECTION]                 [RELIABILITY_SCORE]      |\n"
    "+---------------------------------------------------------------------------------------------------------+"
)
add_code(doc, er_mermaid)

# CHAPTER 4: ER TO RELATIONAL MAPPING
doc.add_page_break()
add_heading_1(doc, "4. ER TO RELATIONAL MAPPING")
add_heading_2(doc, "4.1 STEPS OF ALGORITHM FOR CHOOSEN PROBLEM")
add_para(doc,
    "Step 1: Mapping of Regular (Strong) Entity Types\n"
    "For each strong entity type E in the ER schema, create a relation R that includes all simple attributes of E. Choose one key attribute as Primary Key.\n"
    "• USER(user_id, name, email, role, department) -> PK: user_id\n"
    "• DATA_SOURCE(source_id, source_name, source_type, location) -> PK: source_id\n"
    "• DATASET(dataset_id, dataset_name, description, created_date) -> PK: dataset_id\n"
    "• AI_MODEL(model_id, model_name, model_type, description, created_date) -> PK: model_id\n\n"
    "Step 2: Mapping of Weak Entity Types\n"
    "DATASET_VERSION and MODEL_VERSION are functionally dependent on parent entities. For performance, surrogate auto-increment integer PKs are assigned with UNIQUE candidate keys:\n"
    "• DATASET_VERSION: PK is dataset_version_id, Foreign Key dataset_id references DATASET(dataset_id). Unique constraint: (dataset_id, version_number).\n"
    "• MODEL_VERSION: PK is model_version_id, Foreign Key model_id references AI_MODEL(model_id). Unique constraint: (model_id, version_number).\n\n"
    "Step 3: Mapping of 1:1 Relationship Types\n"
    "For binary 1:1 relationships, the foreign key approach is utilized. The primary key of EVALUATION_RUN is embedded in child entities with a UNIQUE constraint:\n"
    "• EVALUATION_RUN to EVALUATION_RESULT: Embed evaluation_id as FK in EVALUATION_RESULT with UNIQUE constraint. PK is result_id.\n"
    "• EVALUATION_RUN to RELIABILITY_SCORE: Embed evaluation_id as FK in RELIABILITY_SCORE with UNIQUE constraint. PK is reliability_id.\n\n"
    "Step 4: Mapping of 1:N Relationship Types\n"
    "Include the primary key of entity T (1-side) as a foreign key in entity S (N-side):\n"
    "• DATA_SOURCE to DATASET: source_id added as FK in DATASET.\n"
    "• USER to DATASET: owner_id added as FK in DATASET.\n"
    "• USER to AI_MODEL: owner_id added as FK in AI_MODEL.\n"
    "• DATASET to DATA_QUALITY_CHECK: dataset_id added as FK in DATA_QUALITY_CHECK.\n"
    "• DATA_QUALITY_CHECK and DATASET_VERSION to DATA_QUALITY_RESULT: Both quality_check_id and dataset_version_id added as FKs in DATA_QUALITY_RESULT.\n"
    "• MODEL_VERSION and DATASET_VERSION to EVALUATION_RUN: model_version_id, dataset_version_id, and executed_by added as FKs in EVALUATION_RUN.\n"
    "• EVALUATION_RUN to DRIFT_DETECTION: evaluation_id added as FK in DRIFT_DETECTION.\n\n"
    "Step 5: Mapping of M:N Relationship Types\n"
    "The M:N relationship between MODEL_VERSION and DATASET_VERSION is mapped by creating the associative relation EVALUATION_RUN.\n\n"
    "Step 6: Mapping of Multi-valued Attributes\n"
    "All attributes are atomic (1NF satisfied). Multi-valued metrics are stored in dedicated child relations (DRIFT_DETECTION, DATA_QUALITY_RESULT).\n\n"
    "Step 7: Mapping of N-ary Relationships\n"
    "The ternary relationship between MODEL_VERSION, DATASET_VERSION, and USER is mapped directly to EVALUATION_RUN."
)

add_heading_2(doc, "4.2 COMPLETE DIAGRAM OF RELATIONAL MAPPING")
rel_schema_text = (
    "+---------------------------------------------------------------------------------------------------------+\n"
    "|                                     RELATIONAL SCHEMA SPECIFICATION                                     |\n"
    "+---------------------------------------------------------------------------------------------------------+\n"
    "| 1.  USER (user_id [PK], name, email [UQ], role, department)                                            |\n"
    "| 2.  DATA_SOURCE (source_id [PK], source_name, source_type, location)                                    |\n"
    "| 3.  DATASET (dataset_id [PK], dataset_name, description, source_id [FK->DATA_SOURCE],                    |\n"
    "|              owner_id [FK->USER], created_date)                                                         |\n"
    "| 4.  DATASET_VERSION (dataset_version_id [PK], dataset_id [FK->DATASET], version_number,                 |\n"
    "|                       record_count, created_date) [UQ: (dataset_id, version_number)]                    |\n"
    "| 5.  DATA_QUALITY_CHECK (quality_check_id [PK], dataset_id [FK->DATASET], check_name,                    |\n"
    "|                         check_type, threshold)                                                          |\n"
    "| 6.  DATA_QUALITY_RESULT (quality_result_id [PK], quality_check_id [FK->DATA_QUALITY_CHECK],             |\n"
    "|                         dataset_version_id [FK->DATASET_VERSION], score, status, execution_date)       |\n"
    "| 7.  AI_MODEL (model_id [PK], model_name, model_type, description, owner_id [FK->USER], created_date)   |\n"
    "| 8.  MODEL_VERSION (model_version_id [PK], model_id [FK->AI_MODEL], version_number,                     |\n"
    "|                    algorithm, created_date) [UQ: (model_id, version_number)]                            |\n"
    "| 9.  EVALUATION_RUN (evaluation_id [PK], model_version_id [FK->MODEL_VERSION],                           |\n"
    "|                      dataset_version_id [FK->DATASET_VERSION], executed_by [FK->USER],                  |\n"
    "|                      execution_date, status)                                                            |\n"
    "| 10. EVALUATION_RESULT (result_id [PK], evaluation_id [FK->EVALUATION_RUN, UQ], accuracy,                |\n"
    "|                        precision_score, recall_score, f1_score)                                         |\n"
    "| 11. DRIFT_DETECTION (drift_id [PK], evaluation_id [FK->EVALUATION_RUN], drift_score,                    |\n"
    "|                       drift_status, detected_date)                                                      |\n"
    "| 12. RELIABILITY_SCORE (reliability_id [PK], evaluation_id [FK->EVALUATION_RUN, UQ],                     |\n"
    "|                        data_quality_score, model_performance_score, drift_score,                       |\n"
    "|                        overall_score, rating)                                                           |\n"
    "+---------------------------------------------------------------------------------------------------------+"
)
add_code(doc, rel_schema_text)

# CHAPTER 5: DDL STATEMENTS
doc.add_page_break()
add_heading_1(doc, "5. DDL STATEMENTS")
add_heading_2(doc, "STATEMENTS WITH SCREEN SHOTS OF THE TABLE CREATION")
ddl_code = (
    "CREATE DATABASE IF NOT EXISTS ai_model_reliability;\n"
    "USE ai_model_reliability;\n\n"
    "-- 1. USER Table\n"
    "CREATE TABLE user (\n"
    "    user_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    name VARCHAR(100) NOT NULL,\n"
    "    email VARCHAR(150) NOT NULL UNIQUE,\n"
    "    role VARCHAR(50) NOT NULL,\n"
    "    department VARCHAR(100) NOT NULL\n"
    ");\n\n"
    "-- 2. DATA_SOURCE Table\n"
    "CREATE TABLE data_source (\n"
    "    source_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    source_name VARCHAR(150) NOT NULL,\n"
    "    source_type VARCHAR(50) NOT NULL,\n"
    "    location VARCHAR(255)\n"
    ");\n\n"
    "-- 3. DATASET Table\n"
    "CREATE TABLE dataset (\n"
    "    dataset_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    dataset_name VARCHAR(150) NOT NULL,\n"
    "    description TEXT,\n"
    "    source_id INT NOT NULL,\n"
    "    owner_id INT NOT NULL,\n"
    "    created_date DATE NOT NULL,\n"
    "    FOREIGN KEY (source_id) REFERENCES data_source(source_id),\n"
    "    FOREIGN KEY (owner_id) REFERENCES user(user_id)\n"
    ");\n\n"
    "-- 4. DATASET_VERSION Table\n"
    "CREATE TABLE dataset_version (\n"
    "    dataset_version_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    dataset_id INT NOT NULL,\n"
    "    version_number VARCHAR(30) NOT NULL,\n"
    "    record_count BIGINT NOT NULL,\n"
    "    created_date DATE NOT NULL,\n"
    "    UNIQUE (dataset_id, version_number),\n"
    "    FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id)\n"
    ");\n\n"
    "-- 5. DATA_QUALITY_CHECK Table\n"
    "CREATE TABLE data_quality_check (\n"
    "    quality_check_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    dataset_id INT NOT NULL,\n"
    "    check_name VARCHAR(150) NOT NULL,\n"
    "    check_type VARCHAR(50) NOT NULL,\n"
    "    threshold DECIMAL(5,2),\n"
    "    FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id)\n"
    ");\n\n"
    "-- 6. DATA_QUALITY_RESULT Table\n"
    "CREATE TABLE data_quality_result (\n"
    "    quality_result_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    quality_check_id INT NOT NULL,\n"
    "    dataset_version_id INT NOT NULL,\n"
    "    score DECIMAL(5,2) NOT NULL,\n"
    "    status VARCHAR(20) NOT NULL,\n"
    "    execution_date DATETIME NOT NULL,\n"
    "    CHECK (score >= 0 AND score <= 100),\n"
    "    CHECK (status IN ('PASSED','FAILED','WARNING')),\n"
    "    FOREIGN KEY (quality_check_id) REFERENCES data_quality_check(quality_check_id),\n"
    "    FOREIGN KEY (dataset_version_id) REFERENCES dataset_version(dataset_version_id)\n"
    ");\n\n"
    "-- 7. AI_MODEL Table\n"
    "CREATE TABLE ai_model (\n"
    "    model_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    model_name VARCHAR(150) NOT NULL,\n"
    "    model_type VARCHAR(80) NOT NULL,\n"
    "    description TEXT,\n"
    "    owner_id INT NOT NULL,\n"
    "    created_date DATE NOT NULL,\n"
    "    FOREIGN KEY (owner_id) REFERENCES user(user_id)\n"
    ");\n\n"
    "-- 8. MODEL_VERSION Table\n"
    "CREATE TABLE model_version (\n"
    "    model_version_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    model_id INT NOT NULL,\n"
    "    version_number VARCHAR(30) NOT NULL,\n"
    "    algorithm VARCHAR(100) NOT NULL,\n"
    "    created_date DATE NOT NULL,\n"
    "    UNIQUE (model_id, version_number),\n"
    "    FOREIGN KEY (model_id) REFERENCES ai_model(model_id)\n"
    ");\n\n"
    "-- 9. EVALUATION_RUN Table (Central Nexus Entity)\n"
    "CREATE TABLE evaluation_run (\n"
    "    evaluation_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    model_version_id INT NOT NULL,\n"
    "    dataset_version_id INT NOT NULL,\n"
    "    executed_by INT NOT NULL,\n"
    "    execution_date DATETIME NOT NULL,\n"
    "    status VARCHAR(20) NOT NULL,\n"
    "    CHECK (status IN ('COMPLETED','RUNNING','FAILED')),\n"
    "    FOREIGN KEY (model_version_id) REFERENCES model_version(model_version_id),\n"
    "    FOREIGN KEY (dataset_version_id) REFERENCES dataset_version(dataset_version_id),\n"
    "    FOREIGN KEY (executed_by) REFERENCES user(user_id)\n"
    ");\n\n"
    "-- 10. EVALUATION_RESULT Table\n"
    "CREATE TABLE evaluation_result (\n"
    "    result_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    evaluation_id INT NOT NULL UNIQUE,\n"
    "    accuracy DECIMAL(5,2) NOT NULL,\n"
    "    precision_score DECIMAL(5,2) NOT NULL,\n"
    "    recall_score DECIMAL(5,2) NOT NULL,\n"
    "    f1_score DECIMAL(5,2) NOT NULL,\n"
    "    CHECK (accuracy BETWEEN 0 AND 100),\n"
    "    CHECK (precision_score BETWEEN 0 AND 100),\n"
    "    CHECK (recall_score BETWEEN 0 AND 100),\n"
    "    CHECK (f1_score BETWEEN 0 AND 100),\n"
    "    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id)\n"
    ");\n\n"
    "-- 11. DRIFT_DETECTION Table\n"
    "CREATE TABLE drift_detection (\n"
    "    drift_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    evaluation_id INT NOT NULL,\n"
    "    drift_score DECIMAL(6,4) NOT NULL,\n"
    "    drift_status VARCHAR(20) NOT NULL,\n"
    "    detected_date DATETIME NOT NULL,\n"
    "    CHECK (drift_score >= 0),\n"
    "    CHECK (drift_status IN ('LOW','MEDIUM','HIGH')),\n"
    "    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id)\n"
    ");\n\n"
    "-- 12. RELIABILITY_SCORE Table\n"
    "CREATE TABLE reliability_score (\n"
    "    reliability_id INT PRIMARY KEY AUTO_INCREMENT,\n"
    "    evaluation_id INT NOT NULL UNIQUE,\n"
    "    data_quality_score DECIMAL(5,2) NOT NULL,\n"
    "    model_performance_score DECIMAL(5,2) NOT NULL,\n"
    "    drift_score DECIMAL(5,2) NOT NULL,\n"
    "    overall_score DECIMAL(5,2) NOT NULL,\n"
    "    rating VARCHAR(20) NOT NULL,\n"
    "    CHECK (data_quality_score BETWEEN 0 AND 100),\n"
    "    CHECK (model_performance_score BETWEEN 0 AND 100),\n"
    "    CHECK (drift_score BETWEEN 0 AND 100),\n"
    "    CHECK (overall_score BETWEEN 0 AND 100),\n"
    "    CHECK (rating IN ('LOW','MEDIUM','HIGH')),\n"
    "    FOREIGN KEY (evaluation_id) REFERENCES evaluation_run(evaluation_id)\n"
    ");\n\n"
    "-- Performance B-Tree Indexes\n"
    "CREATE INDEX idx_dataset_source ON dataset(source_id);\n"
    "CREATE INDEX idx_dataset_owner ON dataset(owner_id);\n"
    "CREATE INDEX idx_dataset_version_dataset ON dataset_version(dataset_id);\n"
    "CREATE INDEX idx_quality_result_version ON data_quality_result(dataset_version_id);\n"
    "CREATE INDEX idx_model_owner ON ai_model(owner_id);\n"
    "CREATE INDEX idx_model_version_model ON model_version(model_id);\n"
    "CREATE INDEX idx_evaluation_model ON evaluation_run(model_version_id);\n"
    "CREATE INDEX idx_evaluation_dataset ON evaluation_run(dataset_version_id);\n"
    "CREATE INDEX idx_evaluation_date ON evaluation_run(execution_date);\n"
    "CREATE INDEX idx_drift_evaluation ON drift_detection(evaluation_id);"
)
add_code(doc, ddl_code)

# CHAPTER 6: DML STATEMENTS
doc.add_page_break()
add_heading_1(doc, "6. DML STATEMENTS")
add_heading_2(doc, "STATEMENTS WITH SCREEN SHOTS OF THE TABLE WITH INSERTED VALUES")
dml_code = (
    "-- 1. Populate Users\n"
    "INSERT INTO user (name, email, role, department) VALUES\n"
    "('Mohammed Adaan Hamad', 'pes2ug24cs279@pesu.pes.edu', 'Lead ML Engineer', 'Data Science'),\n"
    "('Navya Kishore Dash', 'pes2ug24cs307@pesu.pes.edu', 'Lead MLOps Engineer', 'Platform Engineering'),\n"
    "('Dr. Shilpa S', 'shilpas@pesu.pes.edu', 'Faculty Advisor', 'Computer Science & Engineering');\n\n"
    "-- 2. Populate Data Sources\n"
    "INSERT INTO data_source (source_name, source_type, location) VALUES\n"
    "('Enterprise Data Lake (S3)', 'Amazon S3', 's3://pesu-mlops-datalake/production/'),\n"
    "('Core Banking Replica', 'PostgreSQL DB', 'postgresql://rep-user@db.bank.internal:5432/core_banking'),\n"
    "('CRM Analytics Warehouse', 'Snowflake DW', 'xy12345.ap-south-1.snowflakecomputing.com/crm_analytics');\n\n"
    "-- 3. Populate Datasets\n"
    "INSERT INTO dataset (dataset_name, description, source_id, owner_id, created_date) VALUES\n"
    "('Credit Card Fraud Transactions', 'Synthetic financial dataset with 30 anonymized transaction features', 1, 1, '2026-10-15'),\n"
    "('Telecom Customer Churn', 'Telecommunications subscriber usage and retention telemetry', 3, 2, '2026-10-18');\n\n"
    "-- 4. Populate Dataset Versions\n"
    "INSERT INTO dataset_version (dataset_id, version_number, record_count, created_date) VALUES\n"
    "(1, '1.0', 10000, '2026-10-15'),\n"
    "(1, '2.0', 15000, '2026-10-25'),\n"
    "(2, '1.0', 7043, '2026-10-18'),\n"
    "(2, '1.1', 8500, '2026-10-28');\n\n"
    "-- 5. Populate Data Quality Checks\n"
    "INSERT INTO data_quality_check (dataset_id, check_name, check_type, threshold) VALUES\n"
    "(1, 'Transaction Amount Nullness', 'missing_values', 0.99),\n"
    "(1, 'Transaction ID Uniqueness', 'duplicates', 1.00),\n"
    "(1, 'Amount Non-Negativity', 'numerical_range', 1.00),\n"
    "(2, 'Churn Label Nullness', 'missing_values', 1.00),\n"
    "(2, 'Monthly Charges Range', 'numerical_range', 0.95);\n\n"
    "-- 6. Populate AI Models\n"
    "INSERT INTO ai_model (model_name, model_type, description, owner_id, created_date) VALUES\n"
    "('Financial Fraud Sentinel', 'Binary Classifier', 'Classifies transactions as legitimate or fraudulent', 1, '2026-10-20'),\n"
    "('Customer Retention Oracle', 'Binary Classifier', 'Predicts churn probability for contract subscribers', 2, '2026-10-22');\n\n"
    "-- 7. Populate Model Versions\n"
    "INSERT INTO model_version (model_id, version_number, algorithm, created_date) VALUES\n"
    "(1, '1.0', 'Logistic Regression', '2026-10-20'),\n"
    "(1, '2.0', 'Random Forest', '2026-10-25'),\n"
    "(1, '3.0', 'Decision Tree', '2026-10-28'),\n"
    "(2, '1.0', 'Logistic Regression', '2026-10-22'),\n"
    "(2, '2.0', 'Random Forest', '2026-10-29');\n\n"
    "-- 8. Populate Evaluation Runs & Metrics (Evaluation 1)\n"
    "INSERT INTO evaluation_run (model_version_id, dataset_version_id, executed_by, execution_date, status) VALUES\n"
    "(1, 1, 1, '2026-11-03 12:16:19', 'COMPLETED');\n"
    "INSERT INTO evaluation_result (evaluation_id, accuracy, precision_score, recall_score, f1_score) VALUES\n"
    "(1, 84.36, 83.10, 81.75, 82.42);\n"
    "INSERT INTO drift_detection (evaluation_id, drift_score, drift_status, detected_date) VALUES\n"
    "(1, 0.0425, 'LOW', '2026-11-03 12:16:19');\n"
    "INSERT INTO reliability_score (evaluation_id, data_quality_score, model_performance_score, drift_score, overall_score, rating) VALUES\n"
    "(1, 98.50, 83.08, 91.50, 89.28, 'HIGH');"
)
add_code(doc, dml_code)

# CHAPTER 7: QUERIES
doc.add_page_break()
add_heading_1(doc, "7.  QUERIES")

add_heading_2(doc, "7.1 SIMPLE QUERY WITH GROUP BY, AGRREGATE")
add_para(doc, "Objective: Calculate average accuracy, precision, recall, and F1 score grouped by AI model and algorithm iteration.")
q1 = (
    "SELECT \n"
    "    m.model_name,\n"
    "    mv.version_number,\n"
    "    mv.algorithm,\n"
    "    COUNT(er.evaluation_id) AS total_runs,\n"
    "    ROUND(AVG(res.accuracy), 2) AS avg_accuracy,\n"
    "    ROUND(AVG(res.precision_score), 2) AS avg_precision,\n"
    "    ROUND(AVG(res.recall_score), 2) AS avg_recall,\n"
    "    ROUND(AVG(res.f1_score), 2) AS avg_f1_score\n"
    "FROM model_version mv\n"
    "JOIN ai_model m ON mv.model_id = m.model_id\n"
    "JOIN evaluation_run er ON mv.model_version_id = er.model_version_id\n"
    "JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id\n"
    "WHERE er.status = 'COMPLETED'\n"
    "GROUP BY m.model_name, mv.version_number, mv.algorithm\n"
    "HAVING COUNT(er.evaluation_id) >= 1\n"
    "ORDER BY avg_f1_score DESC;"
)
add_code(doc, q1)

add_heading_2(doc, "7.2 UPDATE OPERATION")
add_para(doc, "Objective: Update the description and record count of a dataset version upon successful ETL data ingestion.")
q2 = (
    "-- Step 1: Update record count in dataset_version\n"
    "UPDATE dataset_version\n"
    "SET record_count = 15500, created_date = CURDATE()\n"
    "WHERE dataset_id = 1 AND version_number = '2.0';\n\n"
    "-- Step 2: Update dataset description\n"
    "UPDATE dataset\n"
    "SET description = 'Augmented credit card transactions including international telemetry'\n"
    "WHERE dataset_id = 1;"
)
add_code(doc, q2)

add_heading_2(doc, "7.3 DELETE OPERATION")
add_para(doc, "Objective: Safely purge obsolete drift detection records for non-critical models older than 180 days while preserving evaluation run lineage.")
q3 = (
    "DELETE FROM drift_detection\n"
    "WHERE evaluation_id IN (\n"
    "    SELECT er.evaluation_id\n"
    "    FROM evaluation_run er\n"
    "    JOIN model_version mv ON er.model_version_id = mv.model_version_id\n"
    "    WHERE mv.algorithm = 'Decision Tree'\n"
    ") AND detected_date < DATE_SUB(NOW(), INTERVAL 180 DAY);"
)
add_code(doc, q3)

add_heading_2(doc, "7.4 CORRELATED QUERY")
add_para(doc, "Objective: Identify the latest evaluation run and its corresponding reliability score for each registered AI model.")
q4 = (
    "SELECT \n"
    "    er.evaluation_id,\n"
    "    m.model_name,\n"
    "    mv.version_number AS model_version,\n"
    "    er.execution_date,\n"
    "    er.status,\n"
    "    res.accuracy,\n"
    "    rs.overall_score AS reliability_score,\n"
    "    rs.rating\n"
    "FROM evaluation_run er\n"
    "JOIN model_version mv ON er.model_version_id = mv.model_version_id\n"
    "JOIN ai_model m ON mv.model_id = m.model_id\n"
    "LEFT JOIN evaluation_result res ON er.evaluation_id = res.evaluation_id\n"
    "LEFT JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id\n"
    "WHERE er.execution_date = (\n"
    "    SELECT MAX(er_inner.execution_date)\n"
    "    FROM evaluation_run er_inner\n"
    "    JOIN model_version mv_inner ON er_inner.model_version_id = mv_inner.model_version_id\n"
    "    WHERE mv_inner.model_id = m.model_id\n"
    ");"
)
add_code(doc, q4)

add_heading_2(doc, "7.5 NESTED QUERY")
add_para(doc, "Objective: Retrieve models whose average reliability score exceeds the overall global platform average reliability score.")
q5 = (
    "SELECT \n"
    "    m.model_id,\n"
    "    m.model_name,\n"
    "    ROUND(AVG(rs.overall_score), 2) AS model_avg_reliability\n"
    "FROM ai_model m\n"
    "JOIN model_version mv ON m.model_id = mv.model_id\n"
    "JOIN evaluation_run er ON mv.model_version_id = er.model_version_id\n"
    "JOIN reliability_score rs ON er.evaluation_id = rs.evaluation_id\n"
    "GROUP BY m.model_id, m.model_name\n"
    "HAVING AVG(rs.overall_score) > (\n"
    "    SELECT AVG(overall_score)\n"
    "    FROM reliability_score\n"
    ");"
)
add_code(doc, q5)

# CHAPTER 8: STORED PROCEDURES, FUNCTIONS AND TRIGGERS
doc.add_page_break()
add_heading_1(doc, "8. STORED PROCEDURES, FUCNTIONS AND TRIGGERS")

add_heading_2(doc, "8.1 STORED PROCEDURES OR FUNCTIONS")
add_para(doc, "1. Stored Function: fn_get_reliability_rating\nMaps a numerical score to trust rating tiers (HIGH, MEDIUM, LOW).")
fn_code = (
    "DELIMITER $$\n\n"
    "CREATE FUNCTION fn_get_reliability_rating(p_score DECIMAL(5,2))\n"
    "RETURNS VARCHAR(20)\n"
    "DETERMINISTIC\n"
    "BEGIN\n"
    "    DECLARE v_rating VARCHAR(20);\n"
    "    IF p_score >= 80.0 THEN\n"
    "        SET v_rating = 'HIGH';\n"
    "    ELSEIF p_score >= 65.0 THEN\n"
    "        SET v_rating = 'MEDIUM';\n"
    "    ELSE\n"
    "        SET v_rating = 'LOW';\n"
    "    END IF;\n"
    "    RETURN v_rating;\n"
    "END$$\n\n"
    "DELIMITER ;"
)
add_code(doc, fn_code)

add_para(doc, "2. Stored Procedure: sp_calculate_composite_reliability\nComputes weighted composite reliability: Overall = (0.35 * DQ) + (0.45 * Model) + (0.20 * Drift).")
sp_code = (
    "DELIMITER $$\n\n"
    "CREATE PROCEDURE sp_calculate_composite_reliability(\n"
    "    IN p_evaluation_id INT\n"
    ")\n"
    "BEGIN\n"
    "    DECLARE v_dataset_version_id INT;\n"
    "    DECLARE v_dq_score DECIMAL(5,2) DEFAULT 85.00;\n"
    "    DECLARE v_accuracy, v_precision, v_recall, v_f1, v_model_score DECIMAL(5,2);\n"
    "    DECLARE v_drift_score DECIMAL(6,4);\n"
    "    DECLARE v_drift_health, v_overall_score DECIMAL(5,2);\n"
    "    DECLARE v_rating VARCHAR(20);\n\n"
    "    -- 1. Identify dataset version\n"
    "    SELECT dataset_version_id INTO v_dataset_version_id\n"
    "    FROM evaluation_run WHERE evaluation_id = p_evaluation_id;\n\n"
    "    -- 2. Calculate average data quality score\n"
    "    SELECT COALESCE(AVG(score), 85.00) INTO v_dq_score\n"
    "    FROM data_quality_result WHERE dataset_version_id = v_dataset_version_id;\n\n"
    "    -- 3. Retrieve model performance metrics\n"
    "    SELECT accuracy, precision_score, recall_score, f1_score\n"
    "    INTO v_accuracy, v_precision, v_recall, v_f1\n"
    "    FROM evaluation_result WHERE evaluation_id = p_evaluation_id;\n"
    "    IF v_accuracy IS NOT NULL THEN\n"
    "        SET v_model_score = (0.40 * v_f1) + (0.30 * v_accuracy) + (0.15 * v_precision) + (0.15 * v_recall);\n"
    "    ELSE\n"
    "        SET v_model_score = 75.00;\n"
    "    END IF;\n\n"
    "    -- 4. Retrieve drift score and apply penalty\n"
    "    SELECT drift_score INTO v_drift_score\n"
    "    FROM drift_detection WHERE evaluation_id = p_evaluation_id\n"
    "    ORDER BY detected_date DESC LIMIT 1;\n"
    "    IF v_drift_score IS NOT NULL THEN\n"
    "        SET v_drift_health = GREATEST(0.00, 100.00 - (v_drift_score * 200.0));\n"
    "    ELSE\n"
    "        SET v_drift_health = 100.00;\n"
    "    END IF;\n\n"
    "    -- 5. Calculate composite overall score\n"
    "    SET v_overall_score = (0.35 * v_dq_score) + (0.45 * v_model_score) + (0.20 * v_drift_health);\n"
    "    SET v_rating = fn_get_reliability_rating(v_overall_score);\n\n"
    "    -- 6. Insert / Update RELIABILITY_SCORE\n"
    "    INSERT INTO reliability_score (\n"
    "        evaluation_id, data_quality_score, model_performance_score, drift_score, overall_score, rating\n"
    "    ) VALUES (\n"
    "        p_evaluation_id, v_dq_score, v_model_score, v_drift_health, v_overall_score, v_rating\n"
    "    ) ON DUPLICATE KEY UPDATE\n"
    "        data_quality_score = VALUES(data_quality_score),\n"
    "        model_performance_score = VALUES(model_performance_score),\n"
    "        drift_score = VALUES(drift_score),\n"
    "        overall_score = VALUES(overall_score),\n"
    "        rating = VALUES(rating);\n"
    "    SELECT * FROM reliability_score WHERE evaluation_id = p_evaluation_id;\n"
    "END$$\n\n"
    "DELIMITER ;"
)
add_code(doc, sp_code)

add_heading_2(doc, "8.2 TRIGGERS")
add_para(doc, "Trigger 1: trg_validate_quality_result_dataset\nEnforces Section 3.6 of specifications: Quality check and Dataset Version must belong to the same Dataset.")
trg1 = (
    "DELIMITER $$\n\n"
    "CREATE TRIGGER trg_validate_quality_result_dataset\n"
    "BEFORE INSERT ON data_quality_result\n"
    "FOR EACH ROW\n"
    "BEGIN\n"
    "    DECLARE v_check_dataset_id INT;\n"
    "    DECLARE v_version_dataset_id INT;\n\n"
    "    SELECT dataset_id INTO v_check_dataset_id\n"
    "    FROM data_quality_check WHERE quality_check_id = NEW.quality_check_id;\n\n"
    "    SELECT dataset_id INTO v_version_dataset_id\n"
    "    FROM dataset_version WHERE dataset_version_id = NEW.dataset_version_id;\n\n"
    "    IF v_check_dataset_id != v_version_dataset_id THEN\n"
    "        SIGNAL SQLSTATE '45000'\n"
    "        SET MESSAGE_TEXT = 'Integrity Error: Quality check and Dataset Version do not belong to the same Dataset!';\n"
    "    END IF;\n"
    "END$$\n\n"
    "DELIMITER ;"
)
add_code(doc, trg1)

add_para(doc, "Trigger 2: trg_prevent_completed_evaluation_deletion\nAudit compliance: Blocks accidental deletion of completed evaluation runs.")
trg2 = (
    "DELIMITER $$\n\n"
    "CREATE TRIGGER trg_prevent_completed_evaluation_deletion\n"
    "BEFORE DELETE ON evaluation_run\n"
    "FOR EACH ROW\n"
    "BEGIN\n"
    "    IF OLD.status = 'COMPLETED' THEN\n"
    "        SIGNAL SQLSTATE '45000'\n"
    "        SET MESSAGE_TEXT = 'Audit Violation: Completed evaluation runs cannot be deleted from the system!';\n"
    "    END IF;\n"
    "END$$\n\n"
    "DELIMITER ;"
)
add_code(doc, trg2)

# CHAPTER 9: FRONT END DEVELOPMENT
doc.add_page_break()
add_heading_1(doc, "9. FRONT END DEVELOPEMNT ")
add_para(doc,
    "The frontend application provides a modern, responsive user interface engineered using React 18, "
    "Vite, Tailwind CSS, and Recharts for dynamic telemetry visualizations. The web client communicates with the "
    "FastAPI backend through modular REST API calls with Axios."
)
add_para(doc,
    "The user interface consists of 11 dedicated application screens:\n"
    "1. Executive Dashboard (DashboardPage.jsx): Displays KPI summary cards, time-series accuracy and drift progression charts, reliability score distribution donuts, and recent evaluation runs.\n"
    "2. Datasets Catalog (DatasetsPage.jsx): Searchable catalog of logical datasets with data source badges, owner attributions, and CSV file upload modal with Pandas tabular profiling.\n"
    "3. Dataset Versions & Lineage (DatasetVersionsPage.jsx): Release history, record counts, null-value percentages per column, data types, and 10-row live CSV table preview.\n"
    "4. Data Quality Management (DataQualityPage.jsx): Configures and runs deterministic quality tests (missingness, uniqueness, ranges), displaying status badges (PASSED, WARNING, FAILED) and score cards.\n"
    "5. AI Model Registry (ModelsPage.jsx): Central inventory of registered models, problem types (Binary Classification), and descriptions.\n"
    "6. Model Iterations & Versions (ModelVersionsPage.jsx): Tracks algorithmic iterations (Logistic Regression, Random Forest, Decision Tree) and Joblib artifact hashes.\n"
    "7. Evaluation Execution & Metrics (EvaluationsPage.jsx): Modal trigger to execute Scikit-learn pipelines. Displays Accuracy, Precision, Recall, F1-score, and an Interactive 2x2 Confusion Matrix Heatmap.\n"
    "8. Side-by-Side Model Comparison (ComparisonPage.jsx): Multi-run comparative matrix highlighting metric differentials (deltas) across versions.\n"
    "9. Feature Drift Analysis (DriftPage.jsx): Visualizes Population Stability Index (PSI) and Kolmogorov-Smirnov p-values for every feature, flagging distribution shifts.\n"
    "10. Reliability Breakdown (ReliabilityPage.jsx): Displays component gauges for Data Quality (35%), Model Performance (45%), and Drift Health (20%), providing actionable recommendations.\n"
    "11. About & Architecture (AboutPage.jsx): Academic attribution for Mohammed Adaan Hamad (PES2UG24CS279) and Navya Kishore Dash (PES2UG24CS307), system environment telemetry, and interactive 12-entity ER map."
)

fe_table_data = [
    ("Dashboard", "src/pages/DashboardPage.jsx", "System KPIs, Recharts time-series trends, reliability donut distribution."),
    ("Datasets", "src/pages/DatasetsPage.jsx", "Dataset catalog, source indicators, CSV file upload with automated profiling."),
    ("Dataset Versions", "src/pages/DatasetVersionsPage.jsx", "Version lineage tree, record counts, null-percentage column stats, CSV preview."),
    ("Data Quality", "src/pages/DataQualityPage.jsx", "Automated DQ checks runner, status badges (PASSED/WARNING/FAILED)."),
    ("AI Models", "src/pages/ModelsPage.jsx", "Model registry, problem type categorization (Binary Classification)."),
    ("Model Versions", "src/pages/ModelVersionsPage.jsx", "Algorithmic release iterations (Logistic Regression, Random Forest, Decision Tree)."),
    ("Evaluations", "src/pages/EvaluationsPage.jsx", "Execution modal, metrics cards, Interactive 2x2 Confusion Matrix Heatmap."),
    ("Comparison", "src/pages/ComparisonPage.jsx", "Side-by-side run comparison of 2–4 models with differential (delta) highlighting."),
    ("Drift Analysis", "src/pages/DriftPage.jsx", "Population Stability Index (PSI) distribution shift tables, KS-test p-values."),
    ("Reliability", "src/pages/ReliabilityPage.jsx", "Weighted formula breakdown, composite score gauges, diagnostic guidance."),
    ("About & System", "src/pages/AboutPage.jsx", "Academic credentials, live runtime environment diagnostics, 12-entity ER map.")
]
add_table_data(doc, [1.5, 2.2, 3.0], ["Screen Name", "Source Component", "Functional Highlights"], fe_table_data)

# REFERENCES
doc.add_page_break()
add_heading_1(doc, "REFERENCES")
refs = [
    "[1] R. Elmasri and S. B. Navathe, Fundamentals of Database Systems, 7th ed. Boston: Pearson, 2016.",
    "[2] A. Silberschatz, H. F. Korth, and S. Sudarshan, Database System Concepts, 7th ed. New York: McGraw-Hill, 2019.",
    "[3] F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
    "[4] W. McKinney, 'Data Structures for Statistical Computing in Python,' in Proceedings of the 9th Python in Science Conference, 2010, pp. 51-56.",
    "[5] B. Yurdakul, 'Selection of the Optimal Population Stability Index (PSI) Cut-Off Value,' Master's Thesis, Middle East Technical University, 2018.",
    "[6] S. Ramirez, FastAPI Documentation, tiangolo.com/fastapi, 2024.",
    "[7] MySQL 8.0 Reference Manual, Oracle Corporation, 2024."
]
for r in refs:
    add_para(doc, r, space_after=4)

add_para(doc, "", space_after=12)
add_heading_2(doc, "GitHub Link:")
p_git = doc.add_paragraph()
r_git = p_git.add_run("https://github.com/Adaan-Ai/ai-model-reliability-platform")
format_run(r_git, font_name="Times New Roman", size_pt=12, bold=True)

# APPENDIX A
doc.add_page_break()
add_heading_1(doc, "APPENDIX A DEFINITIONS, ACRONYMS AND ABBREVIATIONS")
app_data = [
    ("3NF", "Third Normal Form: A relational database schema design ensuring no transitive functional dependencies."),
    ("AUC-ROC", "Area Under the Receiver Operating Characteristic Curve: Measure of binary classifier discrimination."),
    ("B-Tree", "Balanced Tree: Self-balancing search tree index used by MySQL InnoDB for O(log N) lookup latency."),
    ("DDL", "Data Definition Language: SQL syntax for schema creation, modification, and constraint definition."),
    ("DML", "Data Manipulation Language: SQL syntax for querying, inserting, updating, and deleting tuples."),
    ("ER", "Entity-Relationship: High-level conceptual data modeling methodology representing entities and relations."),
    ("F1-Score", "Harmonic mean of precision and recall: F1 = 2 * (Precision * Recall) / (Precision + Recall)."),
    ("FK", "Foreign Key: Attribute referencing the Primary Key of another relation to enforce referential integrity."),
    ("HMR", "Hot Module Replacement: Client bundling feature updating modules in the browser without reloading."),
    ("PK", "Primary Key: Minimal candidate key uniquely identifying a record within a relational table."),
    ("PSI", "Population Stability Index: Metric measuring divergence between baseline and target distributions."),
    ("RDBMS", "Relational Database Management System: Software managing structured data using the relational model.")
]
add_table_data(doc, [1.5, 5.2], ["Acronym", "Formal Definition"], app_data)

# Save document
doc.save(OUTPUT_PATH)
print("SUCCESS: Complete authentic report generated from sample template at:")
print(OUTPUT_PATH)
print("File size:", os.path.getsize(OUTPUT_PATH), "bytes")
