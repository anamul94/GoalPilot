from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalDetailResponse
from app.services import goal_service

router = APIRouter(prefix="/api/goals", tags=["Goals"])


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    status: str | None = Query(None),
    category_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await goal_service.get_goals(db, current_user.id, status, category_id, skip, limit)


@router.post("", response_model=GoalResponse, status_code=201)
async def create_goal(
    data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await goal_service.create_goal(db, current_user.id, data)


@router.get("/{goal_id}", response_model=GoalDetailResponse)
async def get_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await goal_service.get_goal_by_id(db, current_user.id, goal_id)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await goal_service.update_goal(db, current_user.id, goal_id, data)


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await goal_service.delete_goal(db, current_user.id, goal_id)
    return None
