"""
Router: AI Model Registry & Version Management API
Endpoints for registering models, creating model versions, and retrieving lineage (Core Entities 7 & 8).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_model import AIModel
from app.models.model_version import ModelVersion
from app.models.user import User
from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.schemas.model import (
    AIModelCreate, AIModelUpdate, AIModelRead, AIModelDetail,
    ModelVersionCreate, ModelVersionRead, ModelVersionDetail
)
from app.services.model_service import ModelService

router = APIRouter(tags=["AI Models"])

@router.get("/models", response_model=list[AIModelRead])
def get_models(db: Session = Depends(get_db)):
    """List all registered AI models with version counts and latest version tags."""
    models = db.query(AIModel).all()
    results = []
    for m in models:
        v_count = db.query(ModelVersion).filter(ModelVersion.model_id == m.model_id).count()
        latest_v = db.query(ModelVersion).filter(
            ModelVersion.model_id == m.model_id
        ).order_by(ModelVersion.created_date.desc(), ModelVersion.model_version_id.desc()).first()

        item = AIModelRead.model_validate(m)
        item.version_count = v_count
        item.latest_version = latest_v.version_number if latest_v else None
        results.append(item)
    return results

@router.post("/models", response_model=AIModelRead, status_code=status.HTTP_201_CREATED)
def create_model(m_in: AIModelCreate, db: Session = Depends(get_db)):
    """Register a new AI Model."""
    if not db.query(User).filter(User.user_id == m_in.owner_id).first():
        raise HTTPException(status_code=400, detail="Owner user does not exist.")

    model = ModelService.create_model(db, m_in)
    return AIModelRead.model_validate(model)

@router.get("/models/{model_id}", response_model=AIModelDetail)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed model profile with all associated versions."""
    model = db.query(AIModel).filter(AIModel.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found.")

    versions = db.query(ModelVersion).filter(
        ModelVersion.model_id == model_id
    ).order_by(ModelVersion.created_date.desc()).all()

    res = AIModelDetail.model_validate(model)
    res.versions = [ModelVersionRead.model_validate(v) for v in versions]
    return res

@router.put("/models/{model_id}", response_model=AIModelRead)
def update_model(model_id: int, m_up: AIModelUpdate, db: Session = Depends(get_db)):
    """Update AI Model metadata."""
    model = db.query(AIModel).filter(AIModel.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found.")

    if m_up.model_name is not None:
        model.model_name = m_up.model_name
    if m_up.model_type is not None:
        model.model_type = m_up.model_type
    if m_up.description is not None:
        model.description = m_up.description
    if m_up.owner_id is not None:
        model.owner_id = m_up.owner_id

    db.commit()
    db.refresh(model)
    return AIModelRead.model_validate(model)

@router.post("/models/{model_id}/versions", response_model=ModelVersionRead, status_code=status.HTTP_201_CREATED)
def create_version_for_model(model_id: int, req: ModelVersionCreate, db: Session = Depends(get_db)):
    """Register a new version and algorithm for an existing AI model."""
    req.model_id = model_id
    return ModelService.create_model_version(db, req)

@router.get("/models/{model_id}/versions", response_model=list[ModelVersionRead])
def get_versions_for_model(model_id: int, db: Session = Depends(get_db)):
    """List all versions of a specific AI model."""
    return db.query(ModelVersion).filter(
        ModelVersion.model_id == model_id
    ).order_by(ModelVersion.created_date.desc()).all()

@router.get("/model-versions/{version_id}", response_model=ModelVersionDetail)
def get_model_version_detail(version_id: int, db: Session = Depends(get_db)):
    """Inspect model version metrics and evaluation history."""
    mv = db.query(ModelVersion).filter(ModelVersion.model_version_id == version_id).first()
    if not mv:
        raise HTTPException(status_code=404, detail="Model version not found.")

    model = db.query(AIModel).filter(AIModel.model_id == mv.model_id).first()
    
    # Query evaluation stats
    eval_count = db.query(EvaluationRun).filter(
        EvaluationRun.model_version_id == version_id,
        EvaluationRun.status == "COMPLETED"
    ).count()

    latest_eval = db.query(EvaluationRun).filter(
        EvaluationRun.model_version_id == version_id,
        EvaluationRun.status == "COMPLETED"
    ).order_by(EvaluationRun.execution_date.desc()).first()

    res = ModelVersionDetail.model_validate(mv)
    res.model_name = model.model_name if model else None
    res.model_type = model.model_type if model else None
    res.evaluation_count = eval_count

    if latest_eval and latest_eval.result:
        res.latest_accuracy = float(latest_eval.result.accuracy)
        res.latest_f1 = float(latest_eval.result.f1_score)

    return res
