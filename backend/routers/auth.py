from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from backend.database import get_db
from backend.models.user import User
from backend.models.event_log import EventType
from backend.schemas.auth import Token, UserOut, RegisterRequest
from backend.auth.jwt_handler import create_access_token
from backend.auth.dependencies import get_current_user
from backend.services.event_service import log_event
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_ctx.verify(form.password, user.hashed_password):
        logger.warning(f"Failed login attempt: {form.username}")
        await log_event(db, EventType.LOGIN_FAILED, metadata={"attempted_username": form.username})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = create_access_token({"sub": user.username})
    logger.info(f"Login successful: {user.username}")
    await log_event(db, EventType.LOGIN_SUCCESS, user_id=user.id)
    return Token(access_token=token, token_type="bearer")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    hashed = pwd_ctx.hash(request.password)
    user = User(username=request.username, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": user.username})
    logger.info(f"New user registered: {user.username}")
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    logger.info(f"Profile fetched: {current_user.username}")
    return current_user
