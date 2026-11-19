"""
Unit Tests: Data Quality Monitoring Service
Tests deterministic scoring algorithms for missing values, duplicates, types, ranges, schema.
"""

import pandas as pd
import numpy as np
import pytest
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

def test_data_types_check_detects_malformed_numeric_values():
    df = pd.DataFrame({"amount": [str(value) for value in range(9)] + ["not available"]})
    score = QualityService._evaluate_check(df, "data_types")
    assert score == 90.0

def test_numerical_range_detects_outliers_with_contaminated_values():
    df = pd.DataFrame({"amount": list(range(80)) + [1_000_000] * 20})
    score = QualityService._evaluate_check(df, "numerical_range")
    assert score == 80.0

def test_numerical_range_does_not_flag_rare_binary_values():
    df = pd.DataFrame({"is_fraud": [0] * 98 + [1] * 2})
    score = QualityService._evaluate_check(df, "numerical_range")
    assert score == 100.0

@pytest.mark.parametrize(
    "check_type",
    ["missing_values", "duplicates", "data_types", "numerical_range", "categorical_validity", "schema_integrity"],
)
def test_empty_dataset_fails_all_checks(check_type):
    df = pd.DataFrame(columns=["value"])
    assert QualityService._evaluate_check(df, check_type) == 0.0

def test_schema_integrity_detects_duplicate_column_names():
    df = pd.DataFrame([[1, 2]], columns=["value", "value"])
    score = QualityService._evaluate_check(df, "schema_integrity")
    assert score == 90.0

def test_schema_integrity_empty():
    df = pd.DataFrame()
    score = QualityService._evaluate_check(df, "schema_integrity")
    assert score == 0.0

def test_unknown_check_type_raises_error():
    with pytest.raises(ValueError, match="Unsupported quality check type"):
        QualityService._evaluate_check(pd.DataFrame({"a": [1]}), "unknown")
