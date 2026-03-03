from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, Text, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class IdeaAnalytics(Base):
    __tablename__ = "idea_analytics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_log_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("event_logs.id"), nullable=True)
    idea_text: Mapped[str] = mapped_column(Text, nullable=False)
    domain_primary: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain_secondary: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    novelty_verdict: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
