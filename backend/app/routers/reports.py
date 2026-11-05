"""
Router: Downloadable Reports API
Generates structured JSON and tabular CSV audit reports for evaluation runs (Module 10).
"""

import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evaluation_run import EvaluationRun
from app.services.evaluation_service import EvaluationService
from app.services.drift_service import DriftService

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/evaluations/{evaluation_id}")
def get_evaluation_full_report(evaluation_id: int, db: Session = Depends(get_db)):
    """Retrieve the consolidated evaluation report."""
    run = db.query(EvaluationRun).filter(EvaluationRun.evaluation_id == evaluation_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found.")

    rep = EvaluationService.get_evaluation_report(evaluation_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report artifact not found.")
    return rep

@router.get("/evaluations/{evaluation_id}/download")
def download_evaluation_report(
    evaluation_id: int,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db)
):
    """Download evaluation report as CSV or JSON file."""
    run = db.query(EvaluationRun).filter(EvaluationRun.evaluation_id == evaluation_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found.")

    rep = EvaluationService.get_evaluation_report(evaluation_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Report artifact not found.")

    if format == "json":
        import json
        content = json.dumps(rep, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=evaluation_{evaluation_id}_report.json"}
        )

    # Generate Tabular CSV Summary
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Section", "Metric / Attribute", "Value"])
    writer.writerow(["Evaluation", "Evaluation ID", rep.get("evaluation_id")])
    writer.writerow(["Evaluation", "Model Version ID", rep.get("model_version_id")])
    writer.writerow(["Evaluation", "Algorithm", rep.get("algorithm")])
    writer.writerow(["Evaluation", "Dataset Version ID", rep.get("dataset_version_id")])
    writer.writerow(["Evaluation", "Target Column", rep.get("target_column")])
    writer.writerow(["Metrics", "Accuracy (%)", rep.get("accuracy")])
    writer.writerow(["Metrics", "Precision Score (%)", rep.get("precision")])
    writer.writerow(["Metrics", "Recall Score (%)", rep.get("recall")])
    writer.writerow(["Metrics", "F1 Score (%)", rep.get("f1_score")])
    writer.writerow(["Reliability", "Overall Reliability Score", rep.get("reliability_score")])
    writer.writerow(["Reliability", "Reliability Rating", rep.get("reliability_rating")])

    drift_summary = rep.get("drift_summary", {})
    writer.writerow(["Drift", "Overall Drift Score (PSI)", drift_summary.get("overall_drift_score", "N/A")])
    writer.writerow(["Drift", "Drift Status", drift_summary.get("drift_status", "N/A")])

    for r in rep.get("recommendations", []):
        writer.writerow(["Recommendations", "Action Item", r])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=evaluation_{evaluation_id}_summary.csv"}
    )
