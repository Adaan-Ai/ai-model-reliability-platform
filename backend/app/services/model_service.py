"""
AI Model Service
Handles model registration, model version creation, and retrieval.
"""

from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ai_model import AIModel
from app.models.model_version import ModelVersion
from app.schemas.model import AIModelCreate, AIModelUpdate, ModelVersionCreate

class ModelService:
    @staticmethod
    def create_model(db: Session, req: AIModelCreate) -> AIModel:
        model = AIModel(
            model_name=req.model_name,
            model_type=req.model_type,
            description=req.description,
            owner_id=req.owner_id,
            created_date=req.created_date or date.today()
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    @staticmethod
    def create_model_version(db: Session, req: ModelVersionCreate) -> ModelVersion:
        # Check parent model exists
        model = db.query(AIModel).filter(AIModel.model_id == req.model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="AI Model not found.")

        # Check unique constraint (model_id, version_number)
        existing = db.query(ModelVersion).filter(
            ModelVersion.model_id == req.model_id,
            ModelVersion.version_number == req.version_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version '{req.version_number}' already exists for model '{model.model_name}'."
            )

        mv = ModelVersion(
            model_id=req.model_id,
            version_number=req.version_number,
            algorithm=req.algorithm,
            created_date=req.created_date or date.today()
        )
        db.add(mv)
        db.commit()
        db.refresh(mv)
        return mv
