from pydantic import BaseModel
from datetime import datetime


class ChecklistItemCreate(BaseModel):
    title: str
    order_index: int = 0


class ChecklistItemUpdate(BaseModel):
    title: str | None = None
    order_index: int | None = None


class ChecklistReorder(BaseModel):
    ordered_ids: list[str]


class ChecklistItemResponse(BaseModel):
    id: str
    task_id: str
    title: str
    is_completed: bool
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
