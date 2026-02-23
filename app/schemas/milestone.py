from pydantic import BaseModel
from datetime import datetime
from app.models.milestone import MilestoneStatus


class MilestoneCreate(BaseModel):
    title: str
    order_index: int = 0
    start_date: datetime | None = None
    end_date: datetime | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = None
    order_index: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class MilestoneReorder(BaseModel):
    ordered_ids: list[str]


class MilestoneResponse(BaseModel):
    id: str
    goal_id: str
    title: str
    order_index: int
    start_date: datetime | None
    end_date: datetime | None
    status: MilestoneStatus
    progress: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
