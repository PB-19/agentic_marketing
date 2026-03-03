from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.webpage import WebpageRequest, WebpageResult, DeployResult
from backend.agents.webpage_designer_agent import run_webpage_design
from backend.agents.webpage_reviewer_agent import run_design_review_loop
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webpage", tags=["webpage"])


@router.post("/design", response_model=WebpageResult)
async def design_webpage(request: WebpageRequest, current_user: User = Depends(get_current_user)):
    logger.info(f"Webpage design request from {current_user.username}")
    try:
        return await run_webpage_design(request)
    except Exception as e:
        logger.error(f"WebpageDesignerAgent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webpage designer agent error")


@router.post("/design-and-deploy", response_model=DeployResult)
async def design_and_deploy(request: WebpageRequest, current_user: User = Depends(get_current_user)):
    """Full pipeline: design → review loop (max 3 iterations) → GCS deploy → TinyURL."""
    logger.info(f"Design-and-deploy request from {current_user.username}")
    try:
        return await run_design_review_loop(request)
    except Exception as e:
        logger.error(f"Design-review loop failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Design-and-deploy pipeline error")
