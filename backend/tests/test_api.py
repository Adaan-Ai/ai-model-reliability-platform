"""
Integration Tests: FastAPI REST Endpoints
Tests health check, users, data sources, datasets, and dashboard overview.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2  # seeded users

def test_get_datasets():
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert isinstance(datasets, list)
    assert len(datasets) >= 2

def test_get_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert len(models) >= 2

def test_get_dashboard_overview():
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    overview = response.json()
    assert overview["total_datasets"] >= 2
    assert overview["total_models"] >= 2
    assert overview["total_evaluations"] >= 5
    assert overview["avg_model_accuracy"] > 0
