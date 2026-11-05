"""
Pydantic Schemas: DataSource
"""

from pydantic import BaseModel, ConfigDict

class DataSourceBase(BaseModel):
    source_name: str
    source_type: str
    location: str | None = None

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceRead(DataSourceBase):
    source_id: int
    model_config = ConfigDict(from_attributes=True)
