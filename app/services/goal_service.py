from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate


async def create_goal(db: AsyncSession, user_id: str, data: GoalCreate) -> Goal:
    goal = Goal(user_id=user_id, **data.model_dump())
    db.add(goal)
    await db.flush()
    await db.refresh(goal)
    return goal


async def get_goals(
    db: AsyncSession,
    user_id: str,
    status_filter: str | None = None,
    category_id: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Goal]:
    query = select(Goal).where(Goal.user_id == user_id)

    if status_filter:
        query = query.where(Goal.status == status_filter)
    if category_id:
        query = query.where(Goal.category_id == category_id)

    query = query.order_by(Goal.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_goal_by_id(db: AsyncSession, user_id: str, goal_id: str) -> Goal:
    result = await db.execute(
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == user_id)
        .options(selectinload(Goal.milestones))
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


async def update_goal(db: AsyncSession, user_id: str, goal_id: str, data: GoalUpdate) -> Goal:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)

    await db.flush()
    await db.refresh(goal)
    return goal


async def delete_goal(db: AsyncSession, user_id: str, goal_id: str) -> None:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    await db.delete(goal)
    await db.flush()
