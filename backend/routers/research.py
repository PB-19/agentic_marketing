from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.research import IdeaRequest, ResearchResult
from backend.agents.research_agent import run_research
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResult)
async def research_idea(request: IdeaRequest, current_user: User = Depends(get_current_user)):
    logger.info(f"Research request from {current_user.username}: '{request.idea[:60]}'")
    try:
        return await run_research(request)
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Research agent error")
