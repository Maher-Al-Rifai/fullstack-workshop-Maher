from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
