from pydantic import BaseModel
from datetime import datetime
from app.models.task import TaskStatus, RepeatType


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: datetime | None = None
    due_date: datetime | None = None
    estimated_time: int | None = None  # minutes
    repeat_type: RepeatType = RepeatType.NONE
    reminder_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    due_date: datetime | None = None
    estimated_time: int | None = None
    status: TaskStatus | None = None
    repeat_type: RepeatType | None = None
    reminder_at: datetime | None = None


class TaskResponse(BaseModel):
    id: str
    milestone_id: str
    title: str
    description: str | None
    start_date: datetime | None
    due_date: datetime | None
    estimated_time: int | None
    status: TaskStatus
    repeat_type: RepeatType
    reminder_at: datetime | None
    progress: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Task Notes ---
class TaskNoteCreate(BaseModel):
    content: str


class TaskNoteUpdate(BaseModel):
    content: str


class TaskNoteResponse(BaseModel):
    id: str
    task_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
