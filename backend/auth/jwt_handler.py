from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


def create_access_token(data: dict) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"Token created for subject: {data.get('sub')}")
    return token


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        return None
