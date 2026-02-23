from pydantic import BaseModel
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    color: str | None = None
    icon: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    color: str | None
    icon: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
