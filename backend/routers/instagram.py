from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.instagram import (
    InstagramTrendRequest,
    TrendBrief,
    InstagramGenerateRequest,
    InstagramGenerateResult,
    InstagramPublishRequest,
    InstagramPublishResult,
    PostPublishStatus,
)
from backend.agents.instagram_trend_agent import run_instagram_trend_research
from backend.agents.instagram_post_agent import run_instagram_post_generation
from backend.tools.instagram_post_tool import post_to_instagram
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.event_log import EventType
from backend.services.event_service import log_event
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/instagram", tags=["instagram"])


@router.post("/trends", response_model=TrendBrief)
async def research_trends(
    request: InstagramTrendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research Instagram trends for a given idea and research summary."""
    logger.info(f"Instagram trend research request from {current_user.username}")
    try:
        result = await run_instagram_trend_research(request)
        await log_event(
            db, EventType.INSTAGRAM_TREND_RESEARCH,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100]},
        )
        return result
    except Exception as e:
        logger.error(f"InstagramTrendAgent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Instagram trend research failed")


@router.post("/generate", response_model=InstagramGenerateResult)
async def generate_posts(
    request: InstagramGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate Instagram images and captions using the trend brief."""
    logger.info(f"Instagram generate request from {current_user.username} — {request.num_posts} posts")
    try:
        result = await run_instagram_post_generation(request)
        await log_event(
            db, EventType.INSTAGRAM_GENERATE,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100], "num_posts": request.num_posts},
        )
        return result
    except Exception as e:
        logger.error(f"InstagramPostAgent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Instagram post generation failed")


@router.post("/publish", response_model=InstagramPublishResult)
async def publish_posts(
    request: InstagramPublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Post generated images to Instagram. Credentials are used in-memory only and never logged."""
    if len(request.image_urls) != len(request.captions):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="image_urls and captions must have equal length")

    logger.info(f"Instagram publish request from {current_user.username} — {len(request.image_urls)} posts")

    results: list[PostPublishStatus] = []
    for i, (image_url, caption) in enumerate(zip(request.image_urls, request.captions)):
        post_hashtags = (request.hashtags[i] if request.hashtags and i < len(request.hashtags) else [])
        full_caption = caption + ("\n\n" + " ".join(post_hashtags[:5]) if post_hashtags else "")
        try:
            outcome = await post_to_instagram(
                username=request.username,
                password=request.password,
                image_url=image_url,
                caption=full_caption,
            )
            results.append(PostPublishStatus(image_url=image_url, success=True, media_id=outcome["media_id"]))
        except RuntimeError as e:
            logger.error(f"Instagram post failed for {image_url}: {e}")
            results.append(PostPublishStatus(image_url=image_url, success=False, error=str(e)))

    posted_count = sum(1 for r in results if r.success)
    await log_event(
        db, EventType.INSTAGRAM_PUBLISH,
        user_id=current_user.id,
        metadata={"posted": posted_count, "total": len(results)},
    )
    return InstagramPublishResult(results=results)
