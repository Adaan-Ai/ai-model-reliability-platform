"""
Pydantic Schemas: Dataset and DatasetVersion
"""

from datetime import date
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserRead
from app.schemas.data_source import DataSourceRead

# --- Dataset Version Schemas ---
class DatasetVersionBase(BaseModel):
    version_number: str
    record_count: int

class DatasetVersionCreate(DatasetVersionBase):
    dataset_id: int
    created_date: date | None = None

class DatasetVersionRead(DatasetVersionBase):
    dataset_version_id: int
    dataset_id: int
    created_date: date
    model_config = ConfigDict(from_attributes=True)

class DatasetVersionDetail(DatasetVersionRead):
    dataset_name: str | None = None
    file_exists: bool = False
    columns: list[str] = []
    numerical_columns: list[str] = []
    categorical_columns: list[str] = []
    preview: list[dict] = []
    quality_summary: dict | None = None

# --- Dataset Schemas ---
class DatasetBase(BaseModel):
    dataset_name: str
    description: str | None = None
    source_id: int
    owner_id: int

class DatasetCreate(DatasetBase):
    created_date: date | None = None

class DatasetUpdate(BaseModel):
    dataset_name: str | None = None
    description: str | None = None
    source_id: int | None = None
    owner_id: int | None = None

class DatasetRead(DatasetBase):
    dataset_id: int
    created_date: date
    source: DataSourceRead | None = None
    owner: UserRead | None = None
    version_count: int = 0
    latest_version: str | None = None
    model_config = ConfigDict(from_attributes=True)

class DatasetDetail(DatasetRead):
    versions: list[DatasetVersionRead] = []
