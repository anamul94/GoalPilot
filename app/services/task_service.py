from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.task import Task, TaskNote, TaskStatus
from app.models.milestone import Milestone
from app.models.goal import Goal
from app.schemas.task import TaskCreate, TaskUpdate, TaskNoteCreate, TaskNoteUpdate
from app.core.progress_engine import recalculate_milestone_progress


async def _verify_milestone_ownership(db: AsyncSession, user_id: str, milestone_id: str) -> Milestone:
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    goal_result = await db.execute(select(Goal).where(Goal.id == milestone.goal_id, Goal.user_id == user_id))
    if not goal_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    return milestone


async def _verify_task_ownership(db: AsyncSession, user_id: str, task_id: str) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await _verify_milestone_ownership(db, user_id, task.milestone_id)
    return task


async def create_task(db: AsyncSession, user_id: str, milestone_id: str, data: TaskCreate) -> Task:
    await _verify_milestone_ownership(db, user_id, milestone_id)

    task = Task(milestone_id=milestone_id, **data.model_dump())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    await recalculate_milestone_progress(db, milestone_id)
    return task


async def get_tasks(db: AsyncSession, user_id: str, milestone_id: str) -> list[Task]:
    await _verify_milestone_ownership(db, user_id, milestone_id)

    result = await db.execute(
        select(Task).where(Task.milestone_id == milestone_id).order_by(Task.created_at)
    )
    return list(result.scalars().all())


async def update_task(db: AsyncSession, user_id: str, task_id: str, data: TaskUpdate) -> Task:
    task = await _verify_task_ownership(db, user_id, task_id)

    update_data = data.model_dump(exclude_unset=True)

    # If manually marking as completed and no checklist, set progress to 100
    if update_data.get("status") == TaskStatus.COMPLETED:
        task.progress = 100.0
    elif update_data.get("status") == TaskStatus.PENDING:
        task.progress = 0.0

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await recalculate_milestone_progress(db, task.milestone_id)
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, user_id: str, task_id: str) -> None:
    task = await _verify_task_ownership(db, user_id, task_id)
    milestone_id = task.milestone_id

    await db.delete(task)
    await db.flush()
    await recalculate_milestone_progress(db, milestone_id)


# --- Task Notes ---
async def create_task_note(db: AsyncSession, user_id: str, task_id: str, data: TaskNoteCreate) -> TaskNote:
    await _verify_task_ownership(db, user_id, task_id)

    note = TaskNote(task_id=task_id, content=data.content)
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


async def get_task_notes(db: AsyncSession, user_id: str, task_id: str) -> list[TaskNote]:
    await _verify_task_ownership(db, user_id, task_id)

    result = await db.execute(
        select(TaskNote).where(TaskNote.task_id == task_id).order_by(TaskNote.created_at.desc())
    )
    return list(result.scalars().all())


async def update_task_note(db: AsyncSession, user_id: str, note_id: str, data: TaskNoteUpdate) -> TaskNote:
    result = await db.execute(select(TaskNote).where(TaskNote.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await _verify_task_ownership(db, user_id, note.task_id)
    note.content = data.content
    await db.flush()
    await db.refresh(note)
    return note


async def delete_task_note(db: AsyncSession, user_id: str, note_id: str) -> None:
    result = await db.execute(select(TaskNote).where(TaskNote.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await _verify_task_ownership(db, user_id, note.task_id)
    await db.delete(note)
    await db.flush()
