from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.webpage import WebpageRequest, WebpageResult, DeployResult
from backend.agents.webpage_designer_agent import run_webpage_design
from backend.agents.webpage_reviewer_agent import run_design_review_loop
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.event_log import EventType
from backend.services.event_service import log_event
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webpage", tags=["webpage"])


@router.post("/design", response_model=WebpageResult)
async def design_webpage(
    request: WebpageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Webpage design request from {current_user.username}")
    try:
        result = await run_webpage_design(request)
        await log_event(
            db, EventType.DESIGN_REQUEST,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100]},
        )
        return result
    except Exception as e:
        logger.error(f"WebpageDesignerAgent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webpage designer agent error")


@router.post("/design-and-deploy", response_model=DeployResult)
async def design_and_deploy(
    request: WebpageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full pipeline: design → review loop (max 3 iterations) → GCS deploy → TinyURL."""
    logger.info(f"Design-and-deploy request from {current_user.username}")
    try:
        result = await run_design_review_loop(request)
        await log_event(
            db, EventType.DEPLOY_REQUEST,
            user_id=current_user.id,
            metadata={
                "idea_preview": request.idea[:100],
                "tiny_url": result.tiny_url,
                "iteration": result.iteration,
            },
        )
        return result
    except Exception as e:
        logger.error(f"Design-review loop failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Design-and-deploy pipeline error")
