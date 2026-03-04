import enum
from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class EventType(str, enum.Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    RESEARCH_QUERY = "RESEARCH_QUERY"
    DESIGN_REQUEST = "DESIGN_REQUEST"
    DEPLOY_REQUEST = "DEPLOY_REQUEST"
    INSTAGRAM_TREND_RESEARCH = "INSTAGRAM_TREND_RESEARCH"
    INSTAGRAM_GENERATE = "INSTAGRAM_GENERATE"
    INSTAGRAM_PUBLISH = "INSTAGRAM_PUBLISH"


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
