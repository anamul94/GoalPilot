from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.task import Task, TaskStatus
from app.models.milestone import Milestone, MilestoneStatus
from app.models.goal import Goal, GoalStatus
from app.models.checklist import ChecklistItem


async def recalculate_task_progress(db: AsyncSession, task_id: str) -> None:
    """Recalculate task progress based on checklist items."""
    total = await db.scalar(
        select(func.count()).where(ChecklistItem.task_id == task_id)
    )

    if total == 0:
        return

    completed = await db.scalar(
        select(func.count()).where(
            ChecklistItem.task_id == task_id,
            ChecklistItem.is_completed == True,
        )
    )

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return

    task.progress = (completed / total) * 100

    # Auto-complete task if all checklist items done
    if completed == total:
        task.status = TaskStatus.COMPLETED
    elif task.status == TaskStatus.COMPLETED and completed < total:
        task.status = TaskStatus.IN_PROGRESS

    await db.flush()
    await recalculate_milestone_progress(db, task.milestone_id)


async def recalculate_milestone_progress(db: AsyncSession, milestone_id: str) -> None:
    """Recalculate milestone progress using weighted average of task progresses."""
    result = await db.execute(select(Task).where(Task.milestone_id == milestone_id))
    tasks = result.scalars().all()

    if not tasks:
        milestone_result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
        milestone = milestone_result.scalar_one_or_none()
        if milestone:
            milestone.progress = 0.0
            await db.flush()
            await recalculate_goal_progress(db, milestone.goal_id)
        return

    # Weighted by estimated_time if available, otherwise equal weight
    total_weight = 0
    weighted_progress = 0.0

    for task in tasks:
        weight = task.estimated_time if task.estimated_time and task.estimated_time > 0 else 1
        total_weight += weight
        weighted_progress += task.progress * weight

    milestone_result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = milestone_result.scalar_one_or_none()
    if not milestone:
        return

    milestone.progress = weighted_progress / total_weight if total_weight > 0 else 0.0

    # Auto-complete milestone if ALL tasks are completed
    all_completed = all(t.status == TaskStatus.COMPLETED for t in tasks)
    if all_completed and len(tasks) > 0:
        milestone.status = MilestoneStatus.COMPLETED
    elif milestone.status == MilestoneStatus.COMPLETED and not all_completed:
        milestone.status = MilestoneStatus.ACTIVE

    await db.flush()
    await recalculate_goal_progress(db, milestone.goal_id)


async def recalculate_goal_progress(db: AsyncSession, goal_id: str) -> None:
    """Recalculate goal progress as average of milestone progresses."""
    result = await db.execute(select(Milestone).where(Milestone.goal_id == goal_id))
    milestones = result.scalars().all()

    goal_result = await db.execute(select(Goal).where(Goal.id == goal_id))
    goal = goal_result.scalar_one_or_none()
    if not goal:
        return

    if not milestones:
        goal.progress = 0.0
        await db.flush()
        return

    goal.progress = sum(m.progress for m in milestones) / len(milestones)

    # Auto-complete goal if ALL milestones are completed
    all_completed = all(m.status == MilestoneStatus.COMPLETED for m in milestones)
    if all_completed and len(milestones) > 0:
        goal.status = GoalStatus.COMPLETED
    elif goal.status == GoalStatus.COMPLETED and not all_completed:
        goal.status = GoalStatus.ACTIVE

    await db.flush()
