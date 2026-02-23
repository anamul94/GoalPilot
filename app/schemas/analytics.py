from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_goals: int
    completed_goals: int
    active_goals: int
    total_milestones: int
    completed_milestones: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int


class GoalProgressItem(BaseModel):
    id: str
    title: str
    progress: float
    status: str
