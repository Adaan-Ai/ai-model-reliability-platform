"""
Unit Tests: Data Quality Monitoring Service
Tests deterministic scoring algorithms for missing values, duplicates, types, ranges, schema.
"""

import pandas as pd
import numpy as np
from app.services.quality_service import QualityService

def test_missing_values_check_clean():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    score = QualityService._evaluate_check(df, "missing_values")
    assert score == 100.0

def test_missing_values_check_with_nulls():
    df = pd.DataFrame({"a": [1, np.nan, 3], "b": [np.nan, "y", "z"]})
    score = QualityService._evaluate_check(df, "missing_values")
    # 2 nulls out of 6 cells -> 33.33% null -> score should be ~66.67
    assert round(score, 1) == 66.7

def test_duplicates_check():
    df = pd.DataFrame({"a": [1, 2, 1], "b": ["x", "y", "x"]})
    score = QualityService._evaluate_check(df, "duplicates")
    # 1 duplicate out of 3 rows -> ~66.67%
    assert round(score, 1) == 66.7

def test_data_types_check():
    df = pd.DataFrame({"numeric_col": [1.0, 2.5, 3.8, 4.2]})
    score = QualityService._evaluate_check(df, "data_types")
    assert score == 100.0

def test_schema_integrity_empty():
    df = pd.DataFrame()
    score = QualityService._evaluate_check(df, "schema_integrity")
    assert score == 0.0
