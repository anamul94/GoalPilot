from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskNoteCreate, TaskNoteUpdate, TaskNoteResponse
from app.services import task_service

router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get("/milestones/{milestone_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    milestone_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.get_tasks(db, current_user.id, milestone_id)


@router.post("/milestones/{milestone_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    milestone_id: str,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.create_task(db, current_user.id, milestone_id, data)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.update_task(db, current_user.id, task_id, data)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await task_service.delete_task(db, current_user.id, task_id)
    return None


# --- Task Notes ---
@router.get("/tasks/{task_id}/notes", response_model=list[TaskNoteResponse])
async def list_task_notes(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.get_task_notes(db, current_user.id, task_id)


@router.post("/tasks/{task_id}/notes", response_model=TaskNoteResponse, status_code=201)
async def create_task_note(
    task_id: str,
    data: TaskNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.create_task_note(db, current_user.id, task_id, data)


@router.patch("/notes/{note_id}", response_model=TaskNoteResponse)
async def update_task_note(
    note_id: str,
    data: TaskNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.update_task_note(db, current_user.id, note_id, data)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_task_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await task_service.delete_task_note(db, current_user.id, note_id)
    return None
