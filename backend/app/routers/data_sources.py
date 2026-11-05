"""
Router: Data Sources API
Endpoints for Data Source registration and listing (Core Entity 2).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.data_source import DataSource
from app.schemas.data_source import DataSourceCreate, DataSourceRead

router = APIRouter(prefix="/data-sources", tags=["Data Sources"])

@router.get("", response_model=list[DataSourceRead])
def get_data_sources(db: Session = Depends(get_db)):
    """List all registered data sources."""
    return db.query(DataSource).all()

@router.post("", response_model=DataSourceRead, status_code=status.HTTP_201_CREATED)
def create_data_source(ds_in: DataSourceCreate, db: Session = Depends(get_db)):
    """Register a new data source."""
    ds = DataSource(
        source_name=ds_in.source_name,
        source_type=ds_in.source_type,
        location=ds_in.location
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds
