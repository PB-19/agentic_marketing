from pydantic import BaseModel
from backend.schemas.research import ResearchResult


class InstagramTrendRequest(BaseModel):
    idea: str
    research: ResearchResult


class TrendingStyles(BaseModel):
    format: str
    visual_style: str
    tone: str


class InfluencerEntry(BaseModel):
    handle: str
    niche: str
    style: str
    why_relevant: str


class CaptionPatterns(BaseModel):
    structure: str
    avg_length: str
    emoji_usage: str
    cta_style: str


class HashtagStrategy(BaseModel):
    volume_mix: str
    top_hashtags: list[str]


class TrendBrief(BaseModel):
    trending_styles: TrendingStyles
    top_influencers: list[InfluencerEntry]
    caption_patterns: CaptionPatterns
    hashtag_strategy: HashtagStrategy
    content_generation_brief: str


class InstagramGenerateRequest(BaseModel):
    idea: str
    trend_brief: TrendBrief
    num_posts: int = 3
    style_preference: str | None = None


class GeneratedPost(BaseModel):
    image_url: str  # GCS public URL
    caption: str
    hashtags: list[str]


class InstagramGenerateResult(BaseModel):
    posts: list[GeneratedPost]


class InstagramPublishRequest(BaseModel):
    image_urls: list[str]  # GCS public URLs
    captions: list[str]
    hashtags: list[list[str]] | None = None  # per-post hashtags; top 5 appended to caption
    username: str
    password: str


class PostPublishStatus(BaseModel):
    image_url: str
    success: bool
    media_id: str | None = None
    error: str | None = None


class InstagramPublishResult(BaseModel):
    results: list[PostPublishStatus]
