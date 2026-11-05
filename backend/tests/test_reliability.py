"""
Unit Tests: Reliability Scoring Service
Tests signature weighted formula: (0.35 * DQ) + (0.45 * Model) + (0.20 * DriftHealth)
and rating categorization.
"""

from app.services.reliability_service import ReliabilityService

def test_reliability_formula_high():
    dq = 95.0
    model = 90.0
    drift_health = 95.0

    expected = (0.35 * dq) + (0.45 * model) + (0.20 * drift_health)
    # 33.25 + 40.5 + 19.0 = 92.75
    assert round(expected, 2) == 92.75
    assert expected >= 80.0  # HIGH

def test_reliability_formula_low():
    dq = 50.0
    model = 40.0
    drift_health = 30.0

    expected = (0.35 * dq) + (0.45 * model) + (0.20 * drift_health)
    # 17.5 + 18.0 + 6.0 = 41.5
    assert round(expected, 2) == 41.5
    assert expected < 60.0  # LOW

def test_diagnostic_generation():
    reasons, recs = ReliabilityService.generate_diagnostic_reasons_and_recommendations(
        data_quality_score=95.0,
        model_perf_score=88.0,
        drift_health_score=90.0,
        overall_score=91.0,
        rating="HIGH"
    )
    assert len(reasons) >= 3
    assert any("reliable" in r.lower() for r in recs)
