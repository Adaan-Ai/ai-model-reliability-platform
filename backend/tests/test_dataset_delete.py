from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import (
    AIModel,
    DataQualityCheck,
    DataQualityResult,
    DataSource,
    Dataset,
    DatasetVersion,
    DriftDetection,
    EvaluationResult,
    EvaluationRun,
    ModelVersion,
    ReliabilityScore,
    User,
)
from app.services.dataset_service import DatasetService


@pytest.fixture
def isolated_client(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    dataset_dir = tmp_path / "datasets"
    report_dir = tmp_path / "reports"
    dataset_dir.mkdir()
    report_dir.mkdir()
    monkeypatch.setattr(settings, "DATASET_STORAGE_PATH", dataset_dir)
    monkeypatch.setattr(settings, "REPORT_STORAGE_PATH", report_dir)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, test_session, dataset_dir, report_dir
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
        engine.dispose()


def test_delete_dataset_removes_dependent_records_and_files(isolated_client):
    client, test_session, _, report_dir = isolated_client
    db = test_session()
    user = User(
        name="Test Owner",
        email="test-owner@example.test",
        role="Engineer",
        department="Testing",
    )
    source = DataSource(source_name="Test Source", source_type="CSV", location=None)
    dataset = Dataset(
        dataset_name="Delete Test",
        description="Temporary dataset for deletion test.",
        owner=user,
        source=source,
        created_date=date.today(),
    )
    version = DatasetVersion(
        dataset=dataset,
        version_number="1.0",
        record_count=2,
        created_date=date.today(),
    )
    quality_check = DataQualityCheck(
        dataset=dataset,
        check_name="Missing Values",
        check_type="missing_values",
        threshold=90,
    )
    quality_result = DataQualityResult(
        quality_check=quality_check,
        dataset_version=version,
        score=100,
        status="PASSED",
        execution_date=datetime.now(),
    )
    model = AIModel(
        model_name="Reusable Test Model",
        model_type="Classification",
        description=None,
        owner=user,
        created_date=date.today(),
    )
    model_version = ModelVersion(
        model=model,
        version_number="1.0",
        algorithm="Random Forest",
        created_date=date.today(),
    )
    evaluation = EvaluationRun(
        model_version=model_version,
        dataset_version=version,
        executor=user,
        execution_date=datetime.now(),
        status="COMPLETED",
    )
    evaluation_result = EvaluationResult(
        evaluation=evaluation,
        accuracy=90,
        precision_score=90,
        recall_score=90,
        f1_score=90,
    )
    drift = DriftDetection(
        evaluation=evaluation,
        drift_score=0,
        drift_status="LOW",
        detected_date=datetime.now(),
    )
    reliability = ReliabilityScore(
        evaluation=evaluation,
        data_quality_score=100,
        model_performance_score=90,
        drift_score=100,
        overall_score=95,
        rating="HIGH",
    )
    db.add_all([
        dataset,
        model,
        quality_result,
        evaluation_result,
        drift,
        reliability,
    ])
    db.commit()
    dataset_id = dataset.dataset_id
    version_id = version.dataset_version_id
    evaluation_id = evaluation.evaluation_id
    model_version_id = model_version.model_version_id
    db.close()

    dataset_file = DatasetService.get_storage_path(dataset_id, "1.0")
    dataset_file.write_text("feature,target\n1,0\n2,1\n", encoding="utf-8")
    evaluation_report = report_dir / f"evaluation_{evaluation_id}_report.json"
    drift_report = report_dir / f"drift_eval_{evaluation_id}.json"
    evaluation_report.write_text("{}", encoding="utf-8")
    drift_report.write_text("{}", encoding="utf-8")

    response = client.delete(f"/api/datasets/{dataset_id}")

    assert response.status_code == 204
    assert client.get(f"/api/datasets/{dataset_id}").status_code == 404
    assert client.get(f"/api/evaluations/{evaluation_id}").status_code == 404
    assert not dataset_file.exists()
    assert not evaluation_report.exists()
    assert not drift_report.exists()

    db = test_session()
    try:
        assert db.query(DatasetVersion).filter_by(dataset_version_id=version_id).count() == 0
        assert db.query(DataQualityCheck).filter_by(dataset_id=dataset_id).count() == 0
        assert db.query(DataQualityResult).filter_by(dataset_version_id=version_id).count() == 0
        assert db.query(EvaluationRun).filter_by(evaluation_id=evaluation_id).count() == 0
        assert db.query(EvaluationResult).filter_by(evaluation_id=evaluation_id).count() == 0
        assert db.query(DriftDetection).filter_by(evaluation_id=evaluation_id).count() == 0
        assert db.query(ReliabilityScore).filter_by(evaluation_id=evaluation_id).count() == 0
        assert db.query(ModelVersion).filter_by(model_version_id=model_version_id).count() == 1
    finally:
        db.close()


def test_delete_missing_dataset_returns_404(isolated_client):
    client, _, _, _ = isolated_client

    response = client.delete("/api/datasets/999999")

    assert response.status_code == 404
