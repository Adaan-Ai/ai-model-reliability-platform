"""
Pydantic Schemas: DataQualityCheck and DataQualityResult
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

# --- Quality Check Schemas ---
class QualityCheckBase(BaseModel):
    dataset_id: int
    check_name: str
    check_type: str
    threshold: Decimal | float | None = Field(default=90.0, ge=0.0, le=100.0)

class QualityCheckCreate(QualityCheckBase):
    pass

class QualityCheckRead(QualityCheckBase):
    quality_check_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Quality Result Schemas ---
class QualityResultBase(BaseModel):
    quality_check_id: int
    dataset_version_id: int
    score: Decimal | float = Field(ge=0.0, le=100.0)
    status: str  # PASSED, WARNING, FAILED
    execution_date: datetime

class QualityResultCreate(QualityResultBase):
    pass

class QualityResultRead(QualityResultBase):
    quality_result_id: int
    check_name: str | None = None
    check_type: str | None = None
    threshold: Decimal | float | None = None
    model_config = ConfigDict(from_attributes=True)

class RunQualityChecksRequest(BaseModel):
    check_ids: list[int] | None = None  # None means execute all registered checks for this dataset
