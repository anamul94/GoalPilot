from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.checklist import ChecklistItemCreate, ChecklistItemUpdate, ChecklistReorder, ChecklistItemResponse
from app.services import checklist_service

router = APIRouter(prefix="/api", tags=["Checklist"])


@router.get("/tasks/{task_id}/checklist", response_model=list[ChecklistItemResponse])
async def list_checklist(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await checklist_service.get_checklist_items(db, current_user.id, task_id)


@router.post("/tasks/{task_id}/checklist", response_model=ChecklistItemResponse, status_code=201)
async def create_checklist_item(
    task_id: str,
    data: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await checklist_service.create_checklist_item(db, current_user.id, task_id, data)


@router.patch("/checklist/{item_id}/toggle", response_model=ChecklistItemResponse)
async def toggle_checklist_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await checklist_service.toggle_checklist_item(db, current_user.id, item_id)


@router.patch("/checklist/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    item_id: str,
    data: ChecklistItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await checklist_service.update_checklist_item(db, current_user.id, item_id, data)


@router.delete("/checklist/{item_id}", status_code=204)
async def delete_checklist_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await checklist_service.delete_checklist_item(db, current_user.id, item_id)
    return None


@router.patch("/tasks/{task_id}/checklist/reorder", response_model=list[ChecklistItemResponse])
async def reorder_checklist(
    task_id: str,
    data: ChecklistReorder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await checklist_service.reorder_checklist(db, current_user.id, task_id, data)
