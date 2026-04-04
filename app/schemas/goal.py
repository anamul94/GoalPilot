from pydantic import BaseModel
from datetime import datetime
from app.models.goal import Priority, GoalStatus


class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    category_id: str | None = None
    priority: Priority = Priority.MEDIUM
    start_date: datetime | None = None
    end_date: datetime | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category_id: str | None = None
    priority: Priority | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: GoalStatus | None = None


class GoalResponse(BaseModel):
    id: str
    title: str
    description: str | None
    category_id: str | None
    priority: Priority
    start_date: datetime | None
    end_date: datetime | None
    status: GoalStatus
    is_active: bool
    progress: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalDetailResponse(GoalResponse):
    milestones: list["MilestoneResponse"] = []




class ActiveGoalTaskSummary(BaseModel):
    task_id: str
    title: str


class ActiveGoalMilestoneSummary(BaseModel):
    milestone_id: str
    title: str
    task_count: int
    tasks: list[ActiveGoalTaskSummary] = []


class ActiveGoalSummary(BaseModel):
    goal_id: str
    title: str
    description: str | None
    is_active: bool
    milestone_count: int
    milestones: list[ActiveGoalMilestoneSummary] = []

# Avoid circular import
from app.schemas.milestone import MilestoneResponse  # noqa: E402
GoalDetailResponse.model_rebuild()
