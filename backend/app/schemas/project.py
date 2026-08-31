from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    is_public: bool = False


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    is_public: bool | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str
    is_public: bool
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str
    task_count: int
    done_count: int
