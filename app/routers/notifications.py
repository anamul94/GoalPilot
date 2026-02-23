from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class FCMTokenRequest(BaseModel):
    fcm_token: str


@router.get("")
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notification_service.get_notifications(db, current_user.id, skip, limit)


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await notification_service.mark_as_read(db, current_user.id, notification_id)


@router.post("/fcm-token", status_code=204)
async def register_fcm_token(
    data: FCMTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await notification_service.register_fcm_token(db, current_user.id, data.fcm_token)
    return None
