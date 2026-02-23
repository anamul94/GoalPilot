from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneReorder, MilestoneResponse
from app.services import milestone_service

router = APIRouter(prefix="/api", tags=["Milestones"])


@router.get("/goals/{goal_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await milestone_service.get_milestones(db, current_user.id, goal_id)


@router.post("/goals/{goal_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def create_milestone(
    goal_id: str,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await milestone_service.create_milestone(db, current_user.id, goal_id, data)


@router.patch("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await milestone_service.update_milestone(db, current_user.id, milestone_id, data)


@router.delete("/milestones/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await milestone_service.delete_milestone(db, current_user.id, milestone_id)
    return None


@router.patch("/goals/{goal_id}/milestones/reorder", response_model=list[MilestoneResponse])
async def reorder_milestones(
    goal_id: str,
    data: MilestoneReorder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await milestone_service.reorder_milestones(db, current_user.id, goal_id, data)
