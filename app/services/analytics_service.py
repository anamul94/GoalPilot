from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.goal import Goal, GoalStatus
from app.models.milestone import Milestone, MilestoneStatus
from app.models.task import Task, TaskStatus


async def get_dashboard_overview(db: AsyncSession, user_id: str) -> dict:
    total_goals = await db.scalar(
        select(func.count()).where(Goal.user_id == user_id)
    ) or 0

    completed_goals = await db.scalar(
        select(func.count()).where(Goal.user_id == user_id, Goal.status == GoalStatus.COMPLETED)
    ) or 0

    active_goals = await db.scalar(
        select(func.count()).where(Goal.user_id == user_id, Goal.status == GoalStatus.ACTIVE)
    ) or 0

    # Get all goal IDs for this user
    goal_ids_result = await db.execute(
        select(Goal.id).where(Goal.user_id == user_id)
    )
    goal_ids = [r[0] for r in goal_ids_result.all()]

    total_milestones = 0
    completed_milestones = 0
    total_tasks = 0
    completed_tasks = 0
    overdue_tasks = 0

    if goal_ids:
        total_milestones = await db.scalar(
            select(func.count()).where(Milestone.goal_id.in_(goal_ids))
        ) or 0

        completed_milestones = await db.scalar(
            select(func.count()).where(
                Milestone.goal_id.in_(goal_ids),
                Milestone.status == MilestoneStatus.COMPLETED,
            )
        ) or 0

        milestone_ids_result = await db.execute(
            select(Milestone.id).where(Milestone.goal_id.in_(goal_ids))
        )
        milestone_ids = [r[0] for r in milestone_ids_result.all()]

        if milestone_ids:
            total_tasks = await db.scalar(
                select(func.count()).where(Task.milestone_id.in_(milestone_ids))
            ) or 0

            completed_tasks = await db.scalar(
                select(func.count()).where(
                    Task.milestone_id.in_(milestone_ids),
                    Task.status == TaskStatus.COMPLETED,
                )
            ) or 0

            overdue_tasks = await db.scalar(
                select(func.count()).where(
                    Task.milestone_id.in_(milestone_ids),
                    Task.status == TaskStatus.OVERDUE,
                )
            ) or 0

    return {
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "active_goals": active_goals,
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
    }


async def get_goal_progress_bars(db: AsyncSession, user_id: str) -> list[dict]:
    result = await db.execute(
        select(Goal).where(Goal.user_id == user_id, Goal.status == GoalStatus.ACTIVE)
        .order_by(Goal.created_at.desc())
    )
    goals = result.scalars().all()

    return [
        {
            "id": g.id,
            "title": g.title,
            "progress": g.progress,
            "status": g.status.value,
        }
        for g in goals
    ]
