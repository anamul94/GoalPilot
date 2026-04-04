from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.goal import Goal, GoalStatus
from app.models.milestone import Milestone
from app.schemas.goal import GoalCreate, GoalUpdate


async def create_goal(db: AsyncSession, user_id: str, data: GoalCreate) -> Goal:
    existing_goal = await db.execute(
        select(Goal.id).where(Goal.user_id == user_id).limit(1)
    )
    is_first_goal = existing_goal.scalar_one_or_none() is None

    goal = Goal(user_id=user_id, is_active=is_first_goal, **data.model_dump())
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

    if update_data.get("status") in {GoalStatus.COMPLETED, GoalStatus.ARCHIVED}:
        goal.is_active = False

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


async def toggle_goal_active(db: AsyncSession, user_id: str, goal_id: str) -> Goal:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    if not goal.is_active and goal.status in {GoalStatus.COMPLETED, GoalStatus.ARCHIVED}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Goal cannot be activated")

    goal.is_active = not goal.is_active
    await db.flush()
    await db.refresh(goal)
    return goal


async def get_active_goals_summary(db: AsyncSession, user_id: str) -> list[dict]:
    result = await db.execute(
        select(Goal)
        .where(Goal.user_id == user_id, Goal.is_active.is_(True))
        .options(selectinload(Goal.milestones).selectinload(Milestone.tasks))
        .order_by(Goal.created_at.desc())
    )
    goals = result.scalars().all()

    summaries: list[dict] = []
    for goal in goals:
        milestones = sorted(goal.milestones, key=lambda m: m.order_index)
        milestone_summaries = []
        for milestone in milestones:
            tasks = sorted(milestone.tasks, key=lambda t: t.created_at)
            task_summaries = [
                {"task_id": task.id, "title": task.title}
                for task in tasks
            ]
            milestone_summaries.append(
                {
                    "milestone_id": milestone.id,
                    "title": milestone.title,
                    "task_count": len(tasks),
                    "tasks": task_summaries,
                }
            )
        summaries.append(
            {
                "goal_id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "is_active": goal.is_active,
                "milestone_count": len(milestones),
                "milestones": milestone_summaries,
            }
        )

    return summaries
