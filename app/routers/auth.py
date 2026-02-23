from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, AuthResponse, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(db, data)
    tokens = auth_service.generate_tokens(user)
    return {"user": user, "tokens": tokens}


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.login_user(db, data)
    tokens = auth_service.generate_tokens(user)
    return {"user": user, "tokens": tokens}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_access_token(db, data.refresh_token)


@router.post("/logout", status_code=204)
async def logout():
    # Client-side token invalidation; optionally blacklist token server-side
    return None
