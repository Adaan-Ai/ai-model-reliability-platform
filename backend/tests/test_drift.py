"""
Unit Tests: Data Drift Service
Tests PSI calculation, zero-drift on identical distributions, and drift sensitivity.
"""

import numpy as np
import pandas as pd
from app.services.drift_service import DriftService

def test_psi_identical_distributions():
    np.random.seed(42)
    expected = np.random.normal(50, 10, 1000)
    actual = expected.copy()
    psi = DriftService.calculate_psi(expected, actual)
    assert psi < 0.05  # Identical data should have negligible PSI

def test_psi_shifted_distributions():
    np.random.seed(42)
    expected = np.random.normal(50, 10, 1000)
    # Significant mean shift from 50 to 80
    actual = np.random.normal(80, 10, 1000)
    psi = DriftService.calculate_psi(expected, actual)
    assert psi > 0.25  # Should easily trigger HIGH drift

def test_categorical_psi():
    s_expected = pd.Series(["A"] * 500 + ["B"] * 500)
    s_actual = pd.Series(["A"] * 100 + ["B"] * 900)
    psi = DriftService.calculate_categorical_psi(s_expected, s_actual)
    assert psi > 0.20
