from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import DashboardOverview, GoalProgressItem
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=DashboardOverview)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_dashboard_overview(db, current_user.id)


@router.get("/goal-progress", response_model=list[GoalProgressItem])
async def get_goal_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await analytics_service.get_goal_progress_bars(db, current_user.id)
