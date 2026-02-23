from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.milestone import Milestone
from app.models.goal import Goal
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneReorder
from app.core.progress_engine import recalculate_goal_progress


async def _verify_goal_ownership(db: AsyncSession, user_id: str, goal_id: str) -> Goal:
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


async def create_milestone(db: AsyncSession, user_id: str, goal_id: str, data: MilestoneCreate) -> Milestone:
    await _verify_goal_ownership(db, user_id, goal_id)

    milestone = Milestone(goal_id=goal_id, **data.model_dump())
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)
    return milestone


async def get_milestones(db: AsyncSession, user_id: str, goal_id: str) -> list[Milestone]:
    await _verify_goal_ownership(db, user_id, goal_id)

    result = await db.execute(
        select(Milestone).where(Milestone.goal_id == goal_id).order_by(Milestone.order_index)
    )
    return list(result.scalars().all())


async def update_milestone(db: AsyncSession, user_id: str, milestone_id: str, data: MilestoneUpdate) -> Milestone:
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    # Verify ownership
    await _verify_goal_ownership(db, user_id, milestone.goal_id)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(milestone, key, value)

    await db.flush()
    await db.refresh(milestone)
    return milestone


async def delete_milestone(db: AsyncSession, user_id: str, milestone_id: str) -> None:
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    goal_id = milestone.goal_id
    await _verify_goal_ownership(db, user_id, goal_id)

    await db.delete(milestone)
    await db.flush()
    await recalculate_goal_progress(db, goal_id)


async def reorder_milestones(db: AsyncSession, user_id: str, goal_id: str, data: MilestoneReorder) -> list[Milestone]:
    await _verify_goal_ownership(db, user_id, goal_id)

    for index, milestone_id in enumerate(data.ordered_ids):
        result = await db.execute(select(Milestone).where(Milestone.id == milestone_id, Milestone.goal_id == goal_id))
        milestone = result.scalar_one_or_none()
        if milestone:
            milestone.order_index = index

    await db.flush()

    result = await db.execute(
        select(Milestone).where(Milestone.goal_id == goal_id).order_by(Milestone.order_index)
    )
    return list(result.scalars().all())
