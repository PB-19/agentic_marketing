import asyncio
import json
import re
import uuid

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.schemas.instagram import InstagramGenerateRequest, InstagramGenerateResult, GeneratedPost
from backend.config import settings
from backend.logger import get_logger
from backend.tools.imagen_tool import generate_image
from backend.agents.event_logger import log_agent_event

logger = get_logger(__name__)

_INSTRUCTION = """You are an Instagram creative director and content producer.

Given a product idea, a trend brief, and the number of posts to generate:

For each post produce:
1. A detailed image_prompt for Imagen: subject, visual style, mood, color palette, composition — 2-3 specific sentences.
2. A caption: punchy hook (1 line) + body (2-3 lines of value/storytelling) + CTA. No hashtags in caption.
3. 10-15 hashtags: 1-2 mega, 3-5 mid-tier, 5-8 niche. Match domain and trend brief.

Respond ONLY with valid JSON — no markdown, no explanation:
{
  "posts": [
    {
      "image_prompt": "detailed prompt for image generation",
      "caption": "full caption text",
      "hashtags": ["#tag1", "#tag2"]
    }
  ]
}"""

_post_agent = Agent(
    name="InstagramPostAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction=_INSTRUCTION,
    tools=[],
)

_session_service = InMemorySessionService()


def _build_prompt(request: InstagramGenerateRequest) -> str:
    tb = request.trend_brief
    lines = [
        "## Product Idea",
        request.idea,
        "",
        "## Trend Brief",
        f"**Format**: {tb.trending_styles.format}",
        f"**Visual style**: {tb.trending_styles.visual_style}",
        f"**Tone**: {tb.trending_styles.tone}",
        "",
        f"**Caption structure**: {tb.caption_patterns.structure}",
        f"**Caption length**: {tb.caption_patterns.avg_length}",
        f"**Emoji usage**: {tb.caption_patterns.emoji_usage}",
        f"**CTA style**: {tb.caption_patterns.cta_style}",
        "",
        f"**Hashtag strategy**: {tb.hashtag_strategy.volume_mix}",
        f"**Top hashtags**: {', '.join(tb.hashtag_strategy.top_hashtags)}",
        "",
        "## Content Generation Brief",
        tb.content_generation_brief,
    ]

    if request.style_preference:
        lines += ["", "## User Style Preference", request.style_preference]

    lines += ["", f"Generate {request.num_posts} Instagram posts now."]
    return "\n".join(lines)


async def run_instagram_post_generation(request: InstagramGenerateRequest) -> InstagramGenerateResult:
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name="agentic_marketing",
        user_id="system",
        session_id=session_id,
    )
    runner = Runner(
        agent=_post_agent,
        app_name="agentic_marketing",
        session_service=_session_service,
    )

    message = types.Content(role="user", parts=[types.Part(text=_build_prompt(request))])
    response_text = ""

    logger.info(f"InstagramPostAgent: generating {request.num_posts} posts for '{request.idea[:60]}'")
    async for event in runner.run_async(user_id="system", session_id=session.id, new_message=message):
        log_agent_event(event, logger)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    clean = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
    logger.info(f"InstagramPostAgent: content plan received ({len(clean)} chars)")
    data = json.loads(clean)

    # Orchestrator calls generate_image — reliable, deterministic, never hallucinated
    logger.info(f"InstagramPostAgent: generating {len(data['posts'])} images via Imagen")
    async def _build_post(raw: dict) -> GeneratedPost:
        image_url = await generate_image(raw["image_prompt"])
        return GeneratedPost(
            image_url=image_url,
            caption=raw["caption"],
            hashtags=raw["hashtags"],
        )

    posts = await asyncio.gather(*[_build_post(p) for p in data["posts"]])
    return InstagramGenerateResult(posts=list(posts))
