from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.checklist import ChecklistItem
from app.models.task import Task
from app.models.milestone import Milestone
from app.models.goal import Goal
from app.schemas.checklist import ChecklistItemCreate, ChecklistItemUpdate, ChecklistReorder
from app.core.progress_engine import recalculate_task_progress


async def _verify_task_ownership(db: AsyncSession, user_id: str, task_id: str) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    ms_result = await db.execute(select(Milestone).where(Milestone.id == task.milestone_id))
    milestone = ms_result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    goal_result = await db.execute(select(Goal).where(Goal.id == milestone.goal_id, Goal.user_id == user_id))
    if not goal_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


async def create_checklist_item(db: AsyncSession, user_id: str, task_id: str, data: ChecklistItemCreate) -> ChecklistItem:
    await _verify_task_ownership(db, user_id, task_id)

    item = ChecklistItem(task_id=task_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await recalculate_task_progress(db, task_id)
    await db.refresh(item)
    return item


async def get_checklist_items(db: AsyncSession, user_id: str, task_id: str) -> list[ChecklistItem]:
    await _verify_task_ownership(db, user_id, task_id)

    result = await db.execute(
        select(ChecklistItem).where(ChecklistItem.task_id == task_id).order_by(ChecklistItem.order_index)
    )
    return list(result.scalars().all())


async def toggle_checklist_item(db: AsyncSession, user_id: str, item_id: str) -> ChecklistItem:
    result = await db.execute(select(ChecklistItem).where(ChecklistItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")

    await _verify_task_ownership(db, user_id, item.task_id)

    item.is_completed = not item.is_completed
    await db.flush()
    await recalculate_task_progress(db, item.task_id)
    await db.refresh(item)
    return item


async def update_checklist_item(db: AsyncSession, user_id: str, item_id: str, data: ChecklistItemUpdate) -> ChecklistItem:
    result = await db.execute(select(ChecklistItem).where(ChecklistItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")

    await _verify_task_ownership(db, user_id, item.task_id)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.flush()
    await db.refresh(item)
    return item


async def delete_checklist_item(db: AsyncSession, user_id: str, item_id: str) -> None:
    result = await db.execute(select(ChecklistItem).where(ChecklistItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")

    task_id = item.task_id
    await _verify_task_ownership(db, user_id, task_id)

    await db.delete(item)
    await db.flush()
    await recalculate_task_progress(db, task_id)


async def reorder_checklist(db: AsyncSession, user_id: str, task_id: str, data: ChecklistReorder) -> list[ChecklistItem]:
    await _verify_task_ownership(db, user_id, task_id)

    for index, item_id in enumerate(data.ordered_ids):
        result = await db.execute(
            select(ChecklistItem).where(ChecklistItem.id == item_id, ChecklistItem.task_id == task_id)
        )
        item = result.scalar_one_or_none()
        if item:
            item.order_index = index

    await db.flush()

    result = await db.execute(
        select(ChecklistItem).where(ChecklistItem.task_id == task_id).order_by(ChecklistItem.order_index)
    )
    return list(result.scalars().all())
