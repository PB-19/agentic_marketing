from pydantic import BaseModel


class IdeaRequest(BaseModel):
    idea: str
    reference_url: str | None = None


class Competitor(BaseModel):
    name: str
    strengths: str
    weaknesses: str
    positioning: str


class ResearchResult(BaseModel):
    domain_primary: str
    domain_secondary: list[str]
    novelty_verdict: str
    differentiating_aspects: list[str]
    competitors: list[Competitor]
    marketing_implications: list[str]
