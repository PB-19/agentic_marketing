from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.idea_analytics import IdeaAnalytics
from backend.schemas.analytics import IdeaAnalyticsPage, IdeaAnalyticsOut, AnalyticsSummary, NoveltyCount, DomainCount
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/ideas", response_model=IdeaAnalyticsPage)
async def get_idea_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Paginated list of the current user's idea research history."""
    offset = (page - 1) * page_size

    total_result = await db.execute(
        select(func.count()).where(IdeaAnalytics.user_id == current_user.id)
    )
    total = total_result.scalar_one()

    rows_result = await db.execute(
        select(IdeaAnalytics)
        .where(IdeaAnalytics.user_id == current_user.id)
        .order_by(IdeaAnalytics.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [IdeaAnalyticsOut.model_validate(r) for r in rows_result.scalars().all()]

    return IdeaAnalyticsPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated stats: total queries, novelty breakdown, top domains."""
    rows_result = await db.execute(
        select(IdeaAnalytics).where(IdeaAnalytics.user_id == current_user.id)
    )
    rows = rows_result.scalars().all()

    novelty_counter = Counter(r.novelty_verdict for r in rows)
    domain_counter = Counter(r.domain_primary for r in rows)

    return AnalyticsSummary(
        total_queries=len(rows),
        novelty_breakdown=[NoveltyCount(verdict=k, count=v) for k, v in novelty_counter.most_common()],
        top_domains=[DomainCount(domain=k, count=v) for k, v in domain_counter.most_common(5)],
    )
