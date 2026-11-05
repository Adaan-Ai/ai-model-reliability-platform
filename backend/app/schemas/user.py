"""
Pydantic Schemas: User
"""

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    email: str
    role: str
    department: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: str | None = None
    department: str | None = None

class UserRead(UserBase):
    user_id: int
    model_config = ConfigDict(from_attributes=True)
