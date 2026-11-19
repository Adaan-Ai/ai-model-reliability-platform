import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    for run in h.runs:
        run.font.name = 'Calibri'
        if level == 1:
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(16, 44, 87) # Deep Navy
        elif level == 2:
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 70, 120)
        elif level == 3:
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(50, 50, 50)
    return h

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F6F9")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    # Border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        '<w:left w:val="single" w:sz="16" w:space="0" w:color="1E40AF"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        '</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(tbl, col_widths, headers, data):
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E3A8A") # Navy Blue
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    for row_idx, row_data in enumerate(data):
        row = tbl.add_row()
        bg = "FFFFFF" if row_idx % 2 == 0 else "F8FAFC"
        for col_idx, text in enumerate(row_data):
            c = row.cells[col_idx]
            c.text = str(text)
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=120, right=120)
            p = c.paragraphs[0]
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(33, 37, 41)
                
    for row in tbl.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def build_report():
    doc = docx.Document()
    
    # Page setup - Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(33, 37, 41)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------
    # COVER PAGE
    # ---------------------------------------------------------
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_univ = p_univ.add_run("PES UNIVERSITY\n")
    r_univ.font.size = Pt(20)
    r_univ.font.bold = True
    r_univ.font.color.rgb = RGBColor(16, 44, 87)
    
    r_sub = p_univ.add_run("(Established under Karnataka Act No. 16 of 2013)\nElectronic City Campus, Hosur Road, Bengaluru – 560 100, Karnataka, India\n\n")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    p_mini = doc.add_paragraph()
    p_mini.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_mini = p_mini.add_run("A MINI PROJECT REPORT ON\n")
    r_mini.font.size = Pt(13)
    r_mini.font.bold = True
    r_mini.font.color.rgb = RGBColor(70, 70, 70)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AI MODEL EVALUATION & DATA RELIABILITY PLATFORM\n")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_course = p_course.add_run(
        "Submitted in partial fulfilment of the requirements for the award of degree of\n"
        "Bachelor of Technology in Computer Science & Engineering\n"
        "UE23CS351A – Database Management Systems Laboratory\n\n"
        "AUG – DEC 2026\n"
    )
    r_course.font.size = Pt(11)

    # Student & Guide Table
    tbl_names = doc.add_table(rows=1, cols=2)
    tbl_names.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1, c2 = tbl_names.rows[0].cells
    c1.width = Inches(3.2)
    c2.width = Inches(3.2)
    
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r1 = p1.add_run("Submitted by:\n")
    r1.font.bold = True
    p1.add_run("1. MOHAMMED ADAAN HAMAD\n   SRN: PES2UG24CS279\n\n2. NAVYA KISHORE DASH\n   SRN: PES2UG24CS307\n")
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r2 = p2.add_run("Under the Guidance of:\n")
    r2.font.bold = True
    p2.add_run("Dr. Shilpa S\nAssistant Professor\nDepartment of CSE\nPES University\n")

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(24)
    r_dept = p_dept.add_run(
        "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n"
        "FACULTY OF ENGINEERING — PES UNIVERSITY\n"
        "BENGALURU – 560 100, KARNATAKA, INDIA\n"
    )
    r_dept.font.bold = True
    r_dept.font.size = Pt(11)
    r_dept.font.color.rgb = RGBColor(16, 44, 87)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CERTIFICATE
    # ---------------------------------------------------------
    p_cert_head = doc.add_paragraph()
    p_cert_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c1 = p_cert_head.add_run("PES UNIVERSITY\n")
    r_c1.font.size = Pt(16)
    r_c1.font.bold = True
    r_c1.font.color.rgb = RGBColor(16, 44, 87)
    p_cert_head.add_run("Electronic City Campus, Hosur Road, Bengaluru – 560 100\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n\n")

    h_cert = doc.add_paragraph()
    h_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cert = h_cert.add_run("CERTIFICATE\n")
    r_cert.font.size = Pt(18)
    r_cert.font.bold = True
    r_cert.font.underline = True

    p_cert_body = doc.add_paragraph()
    p_cert_body.paragraph_format.line_spacing = 1.3
    p_cert_body.paragraph_format.space_before = Pt(12)
    p_cert_body.add_run(
        "This is to certify that the mini project entitled "
    )
    r_proj = p_cert_body.add_run('"AI Model Evaluation & Data Reliability Platform" ')
    r_proj.font.bold = True
    p_cert_body.add_run(
        "is a bonafide work carried out by MOHAMMED ADAAN HAMAD (PES2UG24CS279) and "
        "NAVYA KISHORE DASH (PES2UG24CS307) in partial fulfilment for the completion of fifth semester "
        "DBMS Laboratory Project (UE23CS351A) in the Program of Study — Bachelor of Technology in Computer "
        "Science and Engineering under the rules and regulations of PES University, Bengaluru during the academic "
        "period AUG. 2026 – DEC. 2026.\n\n"
        "It is certified that all corrections / suggestions indicated during internal evaluations have been incorporated "
        "in this report. The project has been approved as it satisfies the academic requirements in respect of project work."
    )

    doc.add_paragraph("\n\n")
    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    s1, s2 = tbl_sig.rows[0].cells
    s1.width = Inches(3.2)
    s2.width = Inches(3.2)
    
    ps1 = s1.paragraphs[0]
    ps1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    ps1.add_run("___________________________\nDr. Shilpa S\nAssistant Professor & Guide\nDepartment of CSE, PES University")
    
    ps2 = s2.paragraphs[0]
    ps2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ps2.add_run("___________________________\nDr. Sandesh B J\nProfessor & Chairperson\nDepartment of CSE, PES University")

    doc.add_page_break()

    # ---------------------------------------------------------
    # DECLARATION
    # ---------------------------------------------------------
    h_decl = doc.add_paragraph()
    h_decl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_decl = h_decl.add_run("DECLARATION\n")
    r_decl.font.size = Pt(18)
    r_decl.font.bold = True
    r_decl.font.underline = True

    p_decl = doc.add_paragraph()
    p_decl.paragraph_format.line_spacing = 1.3
    p_decl.paragraph_format.space_before = Pt(12)
    p_decl.add_run(
        'We hereby declare that the DBMS Laboratory Project entitled "AI Model Evaluation & Data Reliability Platform" '
        'has been carried out by us under the guidance of Dr. Shilpa S, Assistant Professor, Department of Computer Science '
        'and Engineering, and submitted in partial fulfilment of the course requirements for the award of degree of '
        'Bachelor of Technology in Computer Science and Engineering of PES University, Bengaluru during the academic '
        'semester AUG – DEC 2026.\n\n'
        'We further declare that this report has not been submitted previously to this or any other university for any '
        'degree or diploma.'
    )

    doc.add_paragraph("\n\n")
    tbl_dec_sig = doc.add_table(rows=1, cols=2)
    tbl_dec_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    ds1, ds2 = tbl_dec_sig.rows[0].cells
    ds1.width = Inches(3.2)
    ds2.width = Inches(3.2)
    
    pds1 = ds1.paragraphs[0]
    pds1.add_run("1. MOHAMMED ADAAN HAMAD\n   SRN: PES2UG24CS279\n   Signature: __________________\n   Date: 19-11-2026")
    
    pds2 = ds2.paragraphs[0]
    pds2.add_run("2. NAVYA KISHORE DASH\n   SRN: PES2UG24CS307\n   Signature: __________________\n   Date: 19-11-2026")

    doc.add_page_break()

    # ---------------------------------------------------------
    # ACKNOWLEDGEMENT
    # ---------------------------------------------------------
    h_ack = doc.add_paragraph()
    h_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ack = h_ack.add_run("ACKNOWLEDGEMENT\n")
    r_ack.font.size = Pt(18)
    r_ack.font.bold = True
    r_ack.font.underline = True

    p_ack = doc.add_paragraph()
    p_ack.paragraph_format.line_spacing = 1.3
    p_ack.paragraph_format.space_before = Pt(12)
    p_ack.add_run(
        "We would like to express our deepest gratitude to our faculty guide, Dr. Shilpa S, Assistant Professor, "
        "Department of Computer Science and Engineering, PES University, for her constant encouragement, invaluable suggestions, "
        "and intellectual guidance throughout the conception, architectural design, and implementation of this UE23CS351A DBMS Laboratory project.\n\n"
        "We take this opportunity to convey our sincere thanks to Dr. Sandesh B J, Professor and Chairperson, Department of "
        "Computer Science and Engineering, PES University, for providing the necessary infrastructural resources and institutional "
        "support to carry out our laboratory assignments and research work.\n\n"
        "We express our profound reverence and gratitude to Prof. Jawahar Doreswamy, Chancellor, PES University, and Dr. Suryaprasad J, "
        "Vice-Chancellor, PES University, for fostering an academic environment that empowers engineering students to pursue excellence, "
        "technological innovation, and research-oriented project development.\n\n"
        "Finally, we express our heartfelt appreciation to our parents, family members, and peers for their continuous moral support, "
        "patience, and enthusiasm during the course of this work."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # ABSTRACT
    # ---------------------------------------------------------
    h_abs = doc.add_paragraph()
    h_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_abs = h_abs.add_run("ABSTRACT\n")
    r_abs.font.size = Pt(18)
    r_abs.font.bold = True
    r_abs.font.underline = True

    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.25
    p_abs.paragraph_format.space_before = Pt(10)
    p_abs.add_run(
        "Modern enterprise organizations increasingly depend on Artificial Intelligence (AI) and Machine Learning (ML) models "
        "for mission-critical operations such as credit risk assessment, financial fraud detection, and customer churn prediction. "
        "However, evaluating models solely in static offline environments is fundamentally insufficient. Production models suffer "
        "from data quality degradation, unmanaged dataset version lineage, and statistical feature drift, leading to silent "
        "catastrophic failures. Without a centralized, normalized database architecture, organizations fail to maintain reproducible "
        "audit trails linking dataset versions, quality metrics, evaluation runs, and drift measurements.\n\n"
        "This project presents the AI Model Evaluation & Data Reliability Platform, a full-stack, enterprise-grade system designed "
        "around a strict Third Normal Form (3NF) relational database in MySQL. The database architecture is grounded on exactly 12 core "
        "relational entities: USER, DATA_SOURCE, DATASET, DATASET_VERSION, DATA_QUALITY_CHECK, DATA_QUALITY_RESULT, AI_MODEL, "
        "MODEL_VERSION, EVALUATION_RUN, EVALUATION_RESULT, DRIFT_DETECTION, and RELIABILITY_SCORE.\n\n"
        "The system incorporates a robust Python/FastAPI analytics backend integrating leak-free Scikit-learn classification pipelines, "
        "automated Pandas tabular profiling, six deterministic data quality validation algorithms (missingness, duplicates, data types, "
        "numerical range, categorical validity, schema integrity), two-sample Kolmogorov-Smirnov hypothesis tests, and Population "
        "Stability Index (PSI) drift detection. A transparent, mathematically grounded composite reliability index computes an overall "
        "trust score: Overall = (0.35 × DQ) + (0.45 × Model) + (0.20 × Drift). The frontend is engineered using React 18, Vite, "
        "Tailwind CSS, and Recharts, providing real-time confusion matrices, version lineage trees, and diagnostic recommendations.\n\n"
        "Stored procedures, functions, and active triggers enforce cross-entity foreign key referential integrity and audit compliance. "
        "All platform metrics are derived from real dataset executions without synthetic mock data, providing an enterprise-caliber "
        "solution that bridges relational database theory with practical AI reliability engineering."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # TABLE OF CONTENTS
    # ---------------------------------------------------------
    h_toc = doc.add_paragraph()
    h_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_toc = h_toc.add_run("TABLE OF CONTENTS\n")
    r_toc.font.size = Pt(18)
    r_toc.font.bold = True
    r_toc.font.underline = True

    toc_data = [
        ("1", "INTRODUCTION", "1"),
        ("2", "PROBLEM DEFINITION", "3"),
        ("3", "ER MODEL", "5"),
        ("4", "ER TO RELATIONAL MAPPING", "8"),
        ("4.1", "Steps of Algorithm for Chosen Problem", "8"),
        ("4.2", "Complete Diagram of Relational Mapping", "11"),
        ("5", "DDL STATEMENTS", "13"),
        ("6", "DML STATEMENTS", "18"),
        ("7", "QUERIES", "22"),
        ("7.1", "Simple Query with GROUP BY, Aggregate", "22"),
        ("7.2", "Update Operation", "24"),
        ("7.3", "Delete Operation", "25"),
        ("7.4", "Correlated Query", "26"),
        ("7.5", "Nested Query", "27"),
        ("8", "STORED PROCEDURES, FUNCTIONS AND TRIGGERS", "29"),
        ("8.1", "Stored Procedures and Functions", "29"),
        ("8.2", "Triggers", "33"),
        ("9", "FRONT END DEVELOPMENT", "36"),
        ("", "REFERENCES / BIBLIOGRAPHY", "42"),
        ("", "APPENDIX A: DEFINITIONS, ACRONYMS AND ABBREVIATIONS", "43"),
        ("", "GITHUB REPOSITORY LINK", "44")
    ]
    tbl_toc = doc.add_table(rows=1, cols=3)
    format_table(tbl_toc, [1.0, 4.7, 0.8], ["Chapter No.", "Title", "Page No."], toc_data)

    doc.add_page_break()

    # ---------------------------------------------------------
    # LIST OF TABLES & LIST OF FIGURES
    # ---------------------------------------------------------
    add_styled_heading(doc, "LIST OF TABLES", level=2)
    tables_list = [
        ("Table 3.1", "Entity Summary and Descriptions", "6"),
        ("Table 4.1", "Relational Mapping Cardinality Rules", "9"),
        ("Table 5.1", "DDL Table Specifications and Constraints", "14"),
        ("Table 6.1", "Sample Populated Records Summary", "19"),
        ("Table 8.1", "Stored Procedures and Functions Summary", "30"),
        ("Table 8.2", "Active Database Triggers Summary", "34"),
        ("Table 9.1", "Frontend Pages and Functional Capabilities", "38"),
        ("Table A.1", "Acronyms and Technical Definitions", "43")
    ]
    tbl_lot = doc.add_table(rows=1, cols=3)
    format_table(tbl_lot, [1.2, 4.5, 0.8], ["Table No.", "Title", "Page No."], tables_list)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    add_styled_heading(doc, "LIST OF FIGURES", level=2)
    figs_list = [
        ("Figure 2.1", "High-Level Architecture of AI Model Evaluation Platform", "4"),
        ("Figure 3.1", "Complete Entity-Relationship (ER) Diagram", "7"),
        ("Figure 4.1", "Relational Schema Diagram with Foreign Key References", "12"),
        ("Figure 7.1", "SQL Query Execution Plan & Results", "28"),
        ("Figure 8.1", "Trigger Execution Flow for Cross-Dataset Integrity", "35"),
        ("Figure 9.1", "React Frontend Dashboard Interface", "39"),
        ("Figure 9.2", "Evaluations Confusion Matrix and Performance Breakdown", "40"),
        ("Figure 9.3", "Population Stability Index Feature Drift Visualization", "41")
    ]
    tbl_lof = doc.add_table(rows=1, cols=3)
    format_table(tbl_lof, [1.2, 4.5, 0.8], ["Figure No.", "Title", "Page No."], figs_list)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # ---------------------------------------------------------
    add_styled_heading(doc, "1. INTRODUCTION", level=1)
    doc.add_paragraph(
        "In the contemporary software engineering landscape, enterprise organizations are experiencing a fundamental "
        "paradigm shift. Rule-based procedural software systems are rapidly being superseded or augmented by Machine Learning "
        "(ML) and Artificial Intelligence (AI) models. These models drive automated decision-making in high-consequence domains "
        "such as financial transaction fraud detection, customer churn prediction, credit risk underwriting, and autonomous diagnostics. "
        "However, unlike traditional software artifacts where source code remains invariant once compiled, machine learning models "
        "are intrinsically dual-natured: their functional correctness and behavioral reliability depend equally on the serialized "
        "model code/weights and the statistical distributions of the data upon which they operate."
    )
    doc.add_paragraph(
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
    doc.add_paragraph(
        "The AI Model Evaluation & Data Reliability Platform solves this fundamental engineering challenge. By establishing an authoritative, "
        "Third Normal Form (3NF) relational database in MySQL as the single source of truth, the platform cohesively models the entire "
        "lifecycle of AI reliability. It bridges the gap between Relational Database Management Systems (RDBMS) and modern Machine Learning "
        "Operations (MLOps). The platform tracks users, data sources, datasets, immutable dataset versions, deterministic data quality checks, "
        "AI models, model iterations, evaluation executions, confusion matrix metrics, Population Stability Index (PSI) drift measurements, "
        "and multi-attribute composite reliability scores."
    )
    doc.add_paragraph(
        "Furthermore, this project is engineered as an educational and industrial benchmark. It strictly rejects simulated or mock data: "
        "every metric displayed on its interactive React/Vite dashboard is calculated via real leak-free Scikit-learn pipelines, deterministic "
        "Pandas quality checks, and real MySQL relational queries, demonstrating how foundational database concepts empower production-grade "
        "data science systems."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 2: PROBLEM DEFINITION
    # ---------------------------------------------------------
    add_styled_heading(doc, "2. PROBLEM DEFINITION", level=1)
    doc.add_paragraph(
        "The objective of this project is to conceptualize, design, normalize, and implement an end-to-end relational database management "
        "system and supporting application platform that addresses the reliability crisis in AI model deployment."
    )
    add_styled_heading(doc, "2.1 Problem Statement", level=2)
    doc.add_paragraph(
        "Organizations increasingly rely on AI and machine-learning models for fraud detection, recommendations, forecasting, customer "
        "support, risk analysis, and other business decisions. As these models evolve, organizations need a reliable way to evaluate model "
        "performance, track model and dataset versions, monitor data quality, and detect changes in data that may reduce model reliability. "
        "Without centralized tracking, it becomes difficult to reproduce an evaluation, compare model versions, identify poor-quality data, "
        "or determine whether a model's performance has degraded. The proposed AI Model Evaluation & Data Reliability Platform uses a "
        "relational database to maintain model versions, dataset versions, evaluation runs, data-quality results, drift measurements, "
        "and reliability scores. The platform provides a structured foundation for analyzing whether an AI model and the data supporting "
        "it are reliable enough for continued use."
    )
    add_styled_heading(doc, "2.2 Specific Objectives", level=2)
    doc.add_paragraph(
        "To achieve a comprehensive solution, the project is structured around five core engineering objectives:\n"
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
    add_styled_heading(doc, "2.3 Scope and Limitations", level=2)
    doc.add_paragraph(
        "The project is architectured as a clean modular monolith to emphasize software maintainability, zero external distributed system "
        "overhead (avoiding Kafka, Spark, or Kubernetes), and complete transparency. The relational schema is the central source of truth. "
        "While deep learning architectures (CNNs, Transformers) are excluded from the scope to maintain focus on relational data management, "
        "the platform supports tabular classification algorithms including Logistic Regression, Random Forests, and Decision Trees."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 3: ER MODEL
    # ---------------------------------------------------------
    add_styled_heading(doc, "3. ER MODEL", level=1)
    doc.add_paragraph(
        "The Conceptual Entity-Relationship (ER) model captures the enterprise domain of AI evaluation and data reliability. "
        "The architecture contains 12 entities, mapped strictly to satisfy Third Normal Form (3NF) requirements without data redundancy."
    )
    
    add_styled_heading(doc, "3.1 Entity Descriptions", level=2)
    ent_data = [
        ("USER", "Represents platform users, data scientists, and engineers who own datasets, register models, and execute evaluations.", "user_id (PK), name, email, role, department"),
        ("DATA_SOURCE", "Represents the origin of data feeds (e.g., PostgreSQL DB, S3 Bucket, Snowflake, CSV upload).", "source_id (PK), source_name, source_type, location"),
        ("DATASET", "Logical entity grouping multiple versions of a business dataset (e.g., Bank Fraud Ingestion).", "dataset_id (PK), dataset_name, description, source_id (FK), owner_id (FK), created_date"),
        ("DATASET_VERSION", "Specific immutable release of a dataset with exact record counts and file path bindings.", "dataset_version_id (PK), dataset_id (FK), version_number, record_count, created_date"),
        ("DATA_QUALITY_CHECK", "Defines deterministic verification rules configured for a logical dataset.", "quality_check_id (PK), dataset_id (FK), check_name, check_type, threshold"),
        ("DATA_QUALITY_RESULT", "The empirical outcome of running a quality check against a specific dataset version.", "quality_result_id (PK), quality_check_id (FK), dataset_version_id (FK), score, status, execution_date"),
        ("AI_MODEL", "Logical registry for an AI/ML model entity (e.g., Financial Fraud Sentinel).", "model_id (PK), model_name, model_type, description, owner_id (FK), created_date"),
        ("MODEL_VERSION", "Algorithmic iteration of an AI model with specific architecture and serialized artifact.", "model_version_id (PK), model_id (FK), version_number, algorithm, created_date"),
        ("EVALUATION_RUN", "Central operational entity representing an experimental run binding a model version to a dataset version.", "evaluation_id (PK), model_version_id (FK), dataset_version_id (FK), executed_by (FK), execution_date, status"),
        ("EVALUATION_RESULT", "Performance classification metrics produced by a completed evaluation run (1:1 with run).", "result_id (PK), evaluation_id (FK/Unique), accuracy, precision_score, recall_score, f1_score"),
        ("DRIFT_DETECTION", "Statistical distribution shift measurements comparing baseline and current features.", "drift_id (PK), evaluation_id (FK), drift_score, drift_status, detected_date"),
        ("RELIABILITY_SCORE", "Consolidated composite trust assessment synthesizing quality, performance, and drift (1:1 with run).", "reliability_id (PK), evaluation_id (FK/Unique), data_quality_score, model_performance_score, drift_score, overall_score, rating")
    ]
    tbl_ent = doc.add_table(rows=1, cols=3)
    format_table(tbl_ent, [1.5, 3.2, 1.8], ["Entity Name", "Description", "Attributes"], ent_data)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    add_styled_heading(doc, "3.2 Relationship Cardinalities and Structural Constraints", level=2)
    doc.add_paragraph(
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

    add_styled_heading(doc, "3.3 Complete ER Diagram", level=2)
    doc.add_paragraph(
        "The conceptual diagram illustrates how EVALUATION_RUN serves as the central nexus connecting the AI model hierarchy, "
        "the dataset hierarchy, and the operational evaluation outputs."
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
    add_code_block(doc, er_mermaid)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 4: ER TO RELATIONAL MAPPING
    # ---------------------------------------------------------
    add_styled_heading(doc, "4. ER TO RELATIONAL MAPPING", level=1)
    doc.add_paragraph(
        "The transformation of the conceptual ER model into a logical relational schema follows the standardized 7-step mapping algorithm. "
        "This formal algorithm systematically maps strong entity types, weak entity types, 1:1 relationships, 1:N relationships, "
        "and M:N relationships into relations while ensuring Third Normal Form (3NF) normalization."
    )
    
    add_styled_heading(doc, "4.1 Steps of Algorithm for Chosen Problem", level=2)
    doc.add_paragraph(
        "Step 1: Mapping of Regular (Strong) Entity Types\n"
        "For each strong entity type E in the ER schema, create a relation R that includes all simple attributes of E. Choose one key attribute as Primary Key.\n"
        "• USER(user_id, name, email, role, department) -> PK: user_id\n"
        "• DATA_SOURCE(source_id, source_name, source_type, location) -> PK: source_id\n"
        "• DATASET(dataset_id, dataset_name, description, created_date) -> PK: dataset_id\n"
        "• AI_MODEL(model_id, model_name, model_type, description, created_date) -> PK: model_id\n\n"
        "Step 2: Mapping of Weak Entity Types\n"
        "In our domain, DATASET_VERSION and MODEL_VERSION are functionally dependent on their parent entities. Although assigned surrogate integer "
        "primary keys for performance, they maintain strict composite candidate keys:\n"
        "• DATASET_VERSION: PK is dataset_version_id, Foreign Key dataset_id references DATASET(dataset_id). Unique constraint: (dataset_id, version_number).\n"
        "• MODEL_VERSION: PK is model_version_id, Foreign Key model_id references AI_MODEL(model_id). Unique constraint: (model_id, version_number).\n\n"
        "Step 3: Mapping of 1:1 Relationship Types\n"
        "For binary 1:1 relationships, the foreign key approach is utilized. The primary key of the parent entity is embedded as a foreign key in the child "
        "entity with a UNIQUE constraint to enforce the 1:1 cardinality:\n"
        "• EVALUATION_RUN to EVALUATION_RESULT: Embed evaluation_id as FK in EVALUATION_RESULT with a UNIQUE constraint. PK is result_id.\n"
        "• EVALUATION_RUN to RELIABILITY_SCORE: Embed evaluation_id as FK in RELIABILITY_SCORE with a UNIQUE constraint. PK is reliability_id.\n\n"
        "Step 4: Mapping of 1:N Relationship Types\n"
        "For each binary 1:N relationship, identify the entity S on the N-side and include the primary key of entity T (1-side) as a foreign key in S:\n"
        "• DATA_SOURCE to DATASET: source_id is added as FK in DATASET referencing DATA_SOURCE(source_id).\n"
        "• USER to DATASET: owner_id is added as FK in DATASET referencing USER(user_id).\n"
        "• USER to AI_MODEL: owner_id is added as FK in AI_MODEL referencing USER(user_id).\n"
        "• DATASET to DATA_QUALITY_CHECK: dataset_id is added as FK in DATA_QUALITY_CHECK referencing DATASET(dataset_id).\n"
        "• DATA_QUALITY_CHECK and DATASET_VERSION to DATA_QUALITY_RESULT: Both quality_check_id and dataset_version_id are added as FKs in DATA_QUALITY_RESULT.\n"
        "• MODEL_VERSION and DATASET_VERSION to EVALUATION_RUN: model_version_id, dataset_version_id, and executed_by (USER) are embedded as FKs in EVALUATION_RUN.\n"
        "• EVALUATION_RUN to DRIFT_DETECTION: evaluation_id is added as FK in DRIFT_DETECTION referencing EVALUATION_RUN(evaluation_id).\n\n"
        "Step 5: Mapping of M:N Relationship Types\n"
        "The M:N relationship between MODEL_VERSION and DATASET_VERSION is mapped by creating a separate lookup relation: EVALUATION_RUN. "
        "EVALUATION_RUN serves as an associative entity capturing intersection data (execution_date, status, executed_by) alongside foreign keys.\n\n"
        "Step 6: Mapping of Multi-valued Attributes\n"
        "All attributes in our design are atomic; hence, no auxiliary multi-valued attribute tables were required (1NF satisfied).\n\n"
        "Step 7: Mapping of N-ary Relationships\n"
        "The ternary relationship between MODEL_VERSION, DATASET_VERSION, and USER is formally realized in EVALUATION_RUN."
    )

    add_styled_heading(doc, "4.2 Complete Diagram of Relational Mapping", level=2)
    doc.add_paragraph(
        "The relational schema diagram specifies primary keys (underlined/bold) and foreign key references across all 12 tables:"
    )
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
    add_code_block(doc, rel_schema_text)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 5: DDL STATEMENTS
    # ---------------------------------------------------------
    add_styled_heading(doc, "5. DDL STATEMENTS", level=1)
    doc.add_paragraph(
        "Data Definition Language (DDL) commands create the database instance, define all twelve tables, enforce domain integrity "
        "via CHECK constraints, establish referential integrity via FOREIGN KEY clauses, and optimize query latency with B-Tree indexes."
    )

    ddl_code = (
        "-- Database Creation\n"
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
        "-- 9. EVALUATION_RUN Table (Central Nexus)\n"
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
        "-- B-Tree Performance Indexes\n"
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
    add_code_block(doc, ddl_code)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 6: DML STATEMENTS
    # ---------------------------------------------------------
    add_styled_heading(doc, "6. DML STATEMENTS", level=1)
    doc.add_paragraph(
        "Data Manipulation Language (DML) statements populate the database with real-world enterprise domain data. "
        "The seeded records comprise users from PES University, real data sources (S3, PostgreSQL), real business datasets "
        "(Financial Fraud & Customer Churn), quality checks, algorithms, and evaluation runs."
    )

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
    add_code_block(doc, dml_code)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 7: QUERIES
    # ---------------------------------------------------------
    add_styled_heading(doc, "7. QUERIES", level=1)
    doc.add_paragraph(
        "This chapter presents SQL queries executed on the platform, showcasing analytical aggregations, "
        "data modifications, correlated subqueries, and nested filtering."
    )

    add_styled_heading(doc, "7.1 Simple Query with GROUP BY, Aggregate", level=2)
    doc.add_paragraph(
        "Objective: Calculate the average accuracy, precision, recall, and F1 score grouped by AI model and algorithm iteration."
    )
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
    add_code_block(doc, q1)

    add_styled_heading(doc, "7.2 Update Operation", level=2)
    doc.add_paragraph(
        "Objective: Update the description and record count of a dataset version upon successful ETL data ingestion."
    )
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
    add_code_block(doc, q2)

    add_styled_heading(doc, "7.3 Delete Operation", level=2)
    doc.add_paragraph(
        "Objective: Safely delete stale drift detection records that are older than 180 days for non-critical models."
    )
    q3 = (
        "DELETE FROM drift_detection\n"
        "WHERE evaluation_id IN (\n"
        "    SELECT er.evaluation_id\n"
        "    FROM evaluation_run er\n"
        "    JOIN model_version mv ON er.model_version_id = mv.model_version_id\n"
        "    WHERE mv.algorithm = 'Decision Tree'\n"
        ") AND detected_date < DATE_SUB(NOW(), INTERVAL 180 DAY);"
    )
    add_code_block(doc, q3)

    add_styled_heading(doc, "7.4 Correlated Query", level=2)
    doc.add_paragraph(
        "Objective: Identify the latest evaluation run and its corresponding reliability score for each registered AI model."
    )
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
    add_code_block(doc, q4)

    add_styled_heading(doc, "7.5 Nested Query", level=2)
    doc.add_paragraph(
        "Objective: Retrieve models whose average reliability score exceeds the overall global platform average reliability score."
    )
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
    add_code_block(doc, q5)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 8: STORED PROCEDURES, FUNCTIONS AND TRIGGERS
    # ---------------------------------------------------------
    add_styled_heading(doc, "8. STORED PROCEDURES, FUNCTIONS AND TRIGGERS", level=1)
    doc.add_paragraph(
        "Database logic encapsulation guarantees that mission-critical business rules, composite score calculations, "
        "and referential validation remain enforced within MySQL independently of external application tiers."
    )

    add_styled_heading(doc, "8.1 Stored Procedures and Functions", level=2)
    doc.add_paragraph(
        "Stored Function: fn_get_reliability_rating\n"
        "Maps a continuous numerical reliability score (0.00 – 100.00) into discrete institutional trust tiers ('HIGH', 'MEDIUM', 'LOW')."
    )
    fn_code = (
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
        "END;"
    )
    add_code_block(doc, fn_code)

    doc.add_paragraph(
        "Stored Procedure: sp_calculate_composite_reliability\n"
        "Automates the calculation of the composite reliability score: retrieves average data quality, computes balanced model performance, "
        "applies drift penalties, computes Overall = (0.35 × DQ) + (0.45 × Model) + (0.20 × Drift), and persists the record."
    )
    sp_code = (
        "CREATE PROCEDURE sp_calculate_composite_reliability(IN p_evaluation_id INT)\n"
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
        "    -- 2. Compute mean DQ score\n"
        "    SELECT COALESCE(AVG(score), 85.00) INTO v_dq_score\n"
        "    FROM data_quality_result WHERE dataset_version_id = v_dataset_version_id;\n\n"
        "    -- 3. Retrieve model metrics\n"
        "    SELECT accuracy, precision_score, recall_score, f1_score\n"
        "    INTO v_accuracy, v_precision, v_recall, v_f1\n"
        "    FROM evaluation_result WHERE evaluation_id = p_evaluation_id;\n"
        "    SET v_model_score = (0.40 * v_f1) + (0.30 * v_accuracy) + (0.15 * v_precision) + (0.15 * v_recall);\n\n"
        "    -- 4. Calculate drift health\n"
        "    SELECT drift_score INTO v_drift_score\n"
        "    FROM drift_detection WHERE evaluation_id = p_evaluation_id\n"
        "    ORDER BY detected_date DESC LIMIT 1;\n"
        "    SET v_drift_health = GREATEST(0.00, 100.00 - (COALESCE(v_drift_score, 0.0) * 200.0));\n\n"
        "    -- 5. Calculate weighted composite score\n"
        "    SET v_overall_score = (0.35 * v_dq_score) + (0.45 * v_model_score) + (0.20 * v_drift_health);\n"
        "    SET v_rating = fn_get_reliability_rating(v_overall_score);\n\n"
        "    -- 6. Insert / Update RELIABILITY_SCORE\n"
        "    INSERT INTO reliability_score (\n"
        "        evaluation_id, data_quality_score, model_performance_score, drift_score, overall_score, rating\n"
        "    ) VALUES (p_evaluation_id, v_dq_score, v_model_score, v_drift_health, v_overall_score, v_rating)\n"
        "    ON DUPLICATE KEY UPDATE\n"
        "        data_quality_score = VALUES(data_quality_score),\n"
        "        model_performance_score = VALUES(model_performance_score),\n"
        "        drift_score = VALUES(drift_score),\n"
        "        overall_score = VALUES(overall_score),\n"
        "        rating = VALUES(rating);\n"
        "END;"
    )
    add_code_block(doc, sp_code)

    add_styled_heading(doc, "8.2 Triggers", level=2)
    doc.add_paragraph(
        "Trigger 1: trg_validate_quality_result_dataset\n"
        "Business Requirement: Section 3.6 of the specification mandates that a quality check and dataset version must belong to the same logical dataset. "
        "This trigger intercepts invalid foreign key combinations before insertion and raises SQLSTATE 45000."
    )
    trg1 = (
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
        "END;"
    )
    add_code_block(doc, trg1)

    doc.add_paragraph(
        "Trigger 2: trg_prevent_completed_evaluation_deletion\n"
        "Audit Trail Requirement: Prevents deletion of completed evaluation runs to ensure historical audit reproducibility."
    )
    trg2 = (
        "CREATE TRIGGER trg_prevent_completed_evaluation_deletion\n"
        "BEFORE DELETE ON evaluation_run\n"
        "FOR EACH ROW\n"
        "BEGIN\n"
        "    IF OLD.status = 'COMPLETED' THEN\n"
        "        SIGNAL SQLSTATE '45000'\n"
        "        SET MESSAGE_TEXT = 'Audit Violation: Completed evaluation runs cannot be deleted from the system!';\n"
        "    END IF;\n"
        "END;"
    )
    add_code_block(doc, trg2)

    doc.add_page_break()

    # ---------------------------------------------------------
    # CHAPTER 9: FRONT END DEVELOPMENT
    # ---------------------------------------------------------
    add_styled_heading(doc, "9. FRONT END DEVELOPMENT", level=1)
    doc.add_paragraph(
        "The frontend application provides a modern, responsive, and intuitive graphical user interface engineered using "
        "React 18, Vite, Tailwind CSS, Recharts for dynamic telemetry visualizations, and Lucide React icons."
    )
    doc.add_paragraph(
        "Architecture & REST Integration:\n"
        "The web client interacts with the FastAPI backend through a modular Axios client (`api.js`) mounted on `/api`. "
        "The application maintains real-time health checks (`/health`), dynamic error boundaries, and reactive state management."
    )
    add_styled_heading(doc, "9.1 Application Screens & Visual Walkthrough", level=2)
    doc.add_paragraph(
        "The user interface consists of 11 dedicated screens:\n"
        "1. Executive Dashboard (DashboardPage.jsx): Displays top-level KPI cards (Total Datasets, Total AI Models, Completed Runs, Avg Reliability), "
        "interactive Recharts line charts tracking accuracy and drift progression, reliability distribution donut charts, and recent evaluation records.\n"
        "2. Datasets Catalog (DatasetsPage.jsx): Searchable catalog of logical datasets with data source badges, owner attributions, and a CSV upload modal "
        "with automated tabular profiling.\n"
        "3. Dataset Versions & Lineage (DatasetVersionsPage.jsx): Inspects release history, record counts, null-value percentages per column, data types, "
        "and a 10-row live CSV table preview.\n"
        "4. Data Quality Management (DataQualityPage.jsx): Configures and runs deterministic quality tests (missingness, uniqueness, ranges), displaying "
        "visual status badges (PASSED in green, WARNING in amber, FAILED in red) and test score cards.\n"
        "5. AI Model Registry (ModelsPage.jsx): Central inventory of registered models, problem types (Binary Classification, Regression), and descriptions.\n"
        "6. Model Iterations & Versions (ModelVersionsPage.jsx): Tracks algorithmic iterations (Logistic Regression, Random Forest, Decision Tree) and Joblib artifact hashes.\n"
        "7. Evaluation Execution & Metrics (EvaluationsPage.jsx): Modal trigger to execute real Scikit-learn pipelines. Displays Accuracy, Precision, Recall, "
        "F1-score, and an interactive 2x2 Confusion Matrix Heatmap (True Negatives, False Positives, False Negatives, True Positives).\n"
        "8. Side-by-Side Model Comparison (ComparisonPage.jsx): Multi-run comparative matrix highlighting metric differentials (deltas) across versions.\n"
        "9. Feature Drift Analysis (DriftPage.jsx): Visualizes Population Stability Index (PSI) and Kolmogorov-Smirnov p-values for every feature, "
        "flagging distribution shifts.\n"
        "10. Reliability Breakdown (ReliabilityPage.jsx): Displays component gauges for Data Quality (35%), Model Performance (45%), and Drift Health (20%), "
        "providing actionable recommendations.\n"
        "11. About & Architecture (AboutPage.jsx): Displays academic credentials for Mohammed Adaan Hamad (PES2UG24CS279) and Navya Kishore Dash (PES2UG24CS307), "
        "system environment telemetry, and an interactive 12-entity ER map."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # REFERENCES & APPENDIX
    # ---------------------------------------------------------
    add_styled_heading(doc, "REFERENCES / BIBLIOGRAPHY", level=1)
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
        p = doc.add_paragraph(r)
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    add_styled_heading(doc, "APPENDIX A: DEFINITIONS, ACRONYMS AND ABBREVIATIONS", level=1)
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
    tbl_app = doc.add_table(rows=1, cols=2)
    format_table(tbl_app, [1.5, 5.0], ["Acronym", "Formal Definition"], app_data)

    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    add_styled_heading(doc, "GITHUB REPOSITORY LINK", level=1)
    p_git = doc.add_paragraph()
    p_git.add_run("The complete source code, database scripts, datasets, and tests are hosted at:\n")
    r_git = p_git.add_run("https://github.com/Adaan-Ai/ai-model-reliability-platform")
    r_git.font.bold = True
    r_git.font.color.rgb = RGBColor(30, 64, 175)
    r_git.font.underline = True

    # Save to project docs directory
    out_dir = r"C:\Users\Mohammed Adaan\ai-model-reliability-platform\docs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "AI_Model_Evaluation_Data_Reliability_Platform_Report.docx")
    doc.save(out_path)
    print(f"Report saved successfully at: {out_path}")
    print(f"File size: {os.path.getsize(out_path)} bytes")

if __name__ == "__main__":
    build_report()
