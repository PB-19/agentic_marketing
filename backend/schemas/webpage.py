from pydantic import BaseModel
from backend.schemas.research import ResearchResult


class WebpageRequest(BaseModel):
    idea: str
    research: ResearchResult
    reference_url: str | None = None
    text_preferences: str | None = None


class WebpageResult(BaseModel):
    html: str


class DeployResult(BaseModel):
    html: str
    gcs_url: str
    tiny_url: str
    iteration: int
    notes: str | None = None
