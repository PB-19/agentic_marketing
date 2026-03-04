import json
import re
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search, FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from backend.schemas.instagram import InstagramTrendRequest, TrendBrief
from backend.config import settings
from backend.logger import get_logger
from backend.tools.search_tools import url_fetch
from backend.agents.event_logger import log_agent_event

logger = get_logger(__name__)

_search_sub_agent = Agent(
    name="TrendSearchSubAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction="Perform web searches using google_search and return the results as-is.",
    tools=[google_search],
)

_INSTRUCTION = """You are an Instagram trend analyst. Given a product idea and its market research summary:

1. Identify trending content styles in this domain on Instagram (format, visual style, tone)
2. Find 3-5 top influencers/creators in this space — note their handle, niche, style, and relevance
3. Analyse caption patterns: structure, length, emoji usage, and CTA style of high-performing posts
4. Determine an effective hashtag strategy: volume mix and top relevant hashtags
5. Write a 2-3 paragraph content generation brief summarising all findings

Use SearchSubAgent with 3-5 targeted queries max. Prioritise content from the last 6 months.

Respond ONLY with valid JSON — no markdown, no explanation:
{
  "trending_styles": {
    "format": "string (e.g. carousel / single image / reel)",
    "visual_style": "string (e.g. minimalist / bold colors / lifestyle)",
    "tone": "string (e.g. inspirational / educational / humorous)"
  },
  "top_influencers": [
    {"handle": "string", "niche": "string", "style": "string", "why_relevant": "string"}
  ],
  "caption_patterns": {
    "structure": "string (e.g. hook → value → CTA)",
    "avg_length": "string (e.g. short / medium / long)",
    "emoji_usage": "string (e.g. heavy / moderate / none)",
    "cta_style": "string (example CTA phrases)"
  },
  "hashtag_strategy": {
    "volume_mix": "string (e.g. 2 mega + 4 mid + 6 niche)",
    "top_hashtags": ["#tag1", "#tag2"]
  },
  "content_generation_brief": "string (2-3 paragraphs)"
}"""

_trend_agent = Agent(
    name="InstagramTrendResearchAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction=_INSTRUCTION,
    tools=[AgentTool(agent=_search_sub_agent), FunctionTool(url_fetch)],
)

_session_service = InMemorySessionService()


def _build_prompt(request: InstagramTrendRequest) -> str:
    r = request.research
    lines = [
        f"## Product Idea",
        f"{request.idea}",
        "",
        f"## Market Research Summary",
        f"**Domain**: {r.domain_primary} | Secondary: {', '.join(r.domain_secondary)}",
        f"**Novelty**: {r.novelty_verdict}",
        f"**Differentiating aspects**: {', '.join(r.differentiating_aspects)}",
        f"**Marketing implications**: {', '.join(r.marketing_implications)}",
        "",
        "**Competitors**:",
    ]
    for c in r.competitors:
        lines.append(f"- {c.name}: {c.positioning}")

    lines += ["", "Research Instagram trends for this idea now."]
    return "\n".join(lines)


async def run_instagram_trend_research(request: InstagramTrendRequest) -> TrendBrief:
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name="agentic_marketing",
        user_id="system",
        session_id=session_id,
    )
    runner = Runner(
        agent=_trend_agent,
        app_name="agentic_marketing",
        session_service=_session_service,
    )

    message = types.Content(role="user", parts=[types.Part(text=_build_prompt(request))])
    response_text = ""

    logger.info(f"InstagramTrendAgent: researching for '{request.idea[:60]}'")
    async for event in runner.run_async(user_id="system", session_id=session.id, new_message=message):
        log_agent_event(event, logger)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    clean = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
    logger.info(f"InstagramTrendAgent: response received ({len(clean)} chars)")
    return TrendBrief(**json.loads(clean))
