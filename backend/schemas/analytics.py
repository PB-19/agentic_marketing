from datetime import datetime
from pydantic import BaseModel


class IdeaAnalyticsOut(BaseModel):
    id: int
    idea_text: str
    domain_primary: str
    domain_secondary: list[str]
    novelty_verdict: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IdeaAnalyticsPage(BaseModel):
    items: list[IdeaAnalyticsOut]
    total: int
    page: int
    page_size: int


class NoveltyCount(BaseModel):
    verdict: str
    count: int


class DomainCount(BaseModel):
    domain: str
    count: int


class AnalyticsSummary(BaseModel):
    total_queries: int
    novelty_breakdown: list[NoveltyCount]
    top_domains: list[DomainCount]
