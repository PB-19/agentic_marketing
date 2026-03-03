from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.event_log import EventLog, EventType
from backend.models.idea_analytics import IdeaAnalytics
from backend.schemas.research import ResearchResult
from backend.logger import get_logger

logger = get_logger(__name__)


async def log_event(
    db: AsyncSession,
    event_type: EventType,
    user_id: int | None = None,
    metadata: dict | None = None,
) -> EventLog | None:
    """Persist a single audit event. Returns the saved row, or None on failure."""
    try:
        event = EventLog(user_id=user_id, event_type=event_type, metadata_=metadata)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    except Exception as e:
        logger.error(f"Failed to log event {event_type}: {e}")
        await db.rollback()
        return None


async def log_idea_analytics(
    db: AsyncSession,
    user_id: int,
    idea_text: str,
    result: ResearchResult,
    event_log_id: int | None = None,
) -> None:
    """Persist structured analytics for a research query."""
    try:
        row = IdeaAnalytics(
            user_id=user_id,
            event_log_id=event_log_id,
            idea_text=idea_text,
            domain_primary=result.domain_primary,
            domain_secondary=result.domain_secondary,
            novelty_verdict=result.novelty_verdict,
        )
        db.add(row)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log idea analytics: {e}")
        await db.rollback()
