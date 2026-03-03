import json
import re
import uuid
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from backend.schemas.research import IdeaRequest, ResearchResult
from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)

_INSTRUCTION = """You are a market research expert. For the given product/project idea:
1. Classify the primary domain and up to 3 secondary domains
2. Assess novelty — verdict must be one of: Novel, Competitive entry, Hybrid
3. Use google_search with 3–5 targeted queries max to research competitors
4. List 3–5 top competitors with their strengths, weaknesses, and positioning
5. Derive actionable marketing implications

Respond ONLY with valid JSON — no markdown, no explanation:
{
  "domain_primary": "string",
  "domain_secondary": ["string"],
  "novelty_verdict": "Novel|Competitive entry|Hybrid",
  "differentiating_aspects": ["string"],
  "competitors": [{"name": "string", "strengths": "string", "weaknesses": "string", "positioning": "string"}],
  "marketing_implications": ["string"]
}"""

research_agent = Agent(
    name="IdeaResearcherAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction=_INSTRUCTION,
    tools=[google_search],
)

_session_service = InMemorySessionService()


async def run_research(request: IdeaRequest) -> ResearchResult:
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name="agentic_marketing",
        user_id="system",
        session_id=session_id,
    )
    runner = Runner(
        agent=research_agent,
        app_name="agentic_marketing",
        session_service=_session_service,
    )

    idea_text = request.idea
    if request.reference_url:
        idea_text += f"\n\nReference URL: {request.reference_url}"

    message = types.Content(role="user", parts=[types.Part(text=idea_text)])
    response_text = ""

    logger.info(f"Running research agent for: '{request.idea[:60]}'")
    async for event in runner.run_async(user_id="system", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    # Strip markdown code fences if model wraps JSON
    clean = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
    logger.info(f"Agent response received: {len(clean)} chars")
    return ResearchResult(**json.loads(clean))
