from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.notification import Notification
from app.models.user import User


async def get_notifications(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 20) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def mark_as_read(db: AsyncSession, user_id: str, notification_id: str) -> Notification:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    await db.flush()
    await db.refresh(notification)
    return notification


async def register_fcm_token(db: AsyncSession, user_id: str, fcm_token: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.fcm_token = fcm_token
        await db.flush()
