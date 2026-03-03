from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.research import IdeaRequest, ResearchResult
from backend.agents.research_agent import run_research
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.event_log import EventType
from backend.services.event_service import log_event, log_idea_analytics
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResult)
async def research_idea(
    request: IdeaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Research request from {current_user.username}: '{request.idea[:60]}'")
    try:
        result = await run_research(request)
        event = await log_event(
            db, EventType.RESEARCH_QUERY,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100]},
        )
        await log_idea_analytics(
            db,
            user_id=current_user.id,
            idea_text=request.idea,
            result=result,
            event_log_id=event.id if event else None,
        )
        return result
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Research agent error")
