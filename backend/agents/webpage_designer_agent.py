import re
import uuid
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types
from backend.schemas.webpage import WebpageRequest, WebpageResult
from backend.config import settings
from backend.logger import get_logger
from backend.tools.search_tools import url_fetch
from backend.agents.event_logger import log_agent_event

logger = get_logger(__name__)

_INSTRUCTION = """You are a senior frontend designer specializing in Material Design 3 static landing pages.

Given a product idea, research summary, and optional user preferences, you will:
1. Build a design plan (color palette, typography, layout sections, component style, tone)
2. If reference images are provided alongside this prompt, they are your PRIMARY visual constraint — your design MUST closely match their layout, color scheme, typography, and overall structure. Do not treat them as loose inspiration.
3. If a reference URL is provided, use url_fetch to fetch the page — treat its visual structure and style as your primary design constraint, not just inspiration. Your page must closely resemble it.
4. Incorporate any user text preferences
5. Generate a complete, self-contained single-file HTML landing page

## Design constraints
- Material Design 3 principles (elevation, color system, typography scale)
- Inline CSS only — no external CDN dependencies required for rendering
- Mobile-responsive layout using CSS Grid/Flexbox
- Sections: Hero, Features/Benefits, About, CTA, Footer (adjust based on research context)

## Output format
Respond with ONLY the raw HTML file — no markdown fences, no explanation.
At the very top of the HTML, include your design plan as an HTML comment block:
<!--
DESIGN PLAN
- Color palette: ...
- Typography: ...
- Layout sections: ...
- Component style: ...
- Tone/mood: ...
- Reference influence: ...
-->
Then the full <!DOCTYPE html> ... </html> page follows immediately."""

_webpage_designer_agent = Agent(
    name="WebpageDesignerAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction=_INSTRUCTION,
    tools=[FunctionTool(url_fetch)],
)

_session_service = InMemorySessionService()


def _build_prompt(request: WebpageRequest) -> str:
    r = request.research
    lines = [
        f"## Product Idea",
        f"{request.idea}",
        "",
        f"## Research Summary",
        f"**Domain**: {r.domain_primary} | Secondary: {', '.join(r.domain_secondary)}",
        f"**Novelty**: {r.novelty_verdict}",
        f"**Differentiating aspects**: {', '.join(r.differentiating_aspects)}",
        f"**Marketing implications**: {', '.join(r.marketing_implications)}",
        "",
        "**Top competitors**:",
    ]
    for c in r.competitors:
        lines.append(f"- {c.name}: strengths={c.strengths} | weaknesses={c.weaknesses} | positioning={c.positioning}")

    if request.reference_url:
        lines += ["", f"**Reference URL** (fetch and treat as primary design constraint — your page must closely resemble it): {request.reference_url}"]
    if request.text_preferences:
        lines += ["", f"**User preferences**: {request.text_preferences}"]

    lines += ["", "Generate the landing page HTML now."]
    return "\n".join(lines)


async def _run_agent(
    prompt: str,
    log_prefix: str,
    reference_parts: list[types.Part] | None = None,
) -> str:
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name="agentic_marketing",
        user_id="system",
        session_id=session_id,
    )
    runner = Runner(
        agent=_webpage_designer_agent,
        app_name="agentic_marketing",
        session_service=_session_service,
    )

    # Reference images go first so the model sees them before the text prompt
    parts: list[types.Part] = (reference_parts or []) + [types.Part(text=prompt)]
    message = types.Content(role="user", parts=parts)
    response_text = ""

    logger.info(f"WebpageDesignerAgent: {log_prefix}")
    async for event in runner.run_async(user_id="system", session_id=session.id, new_message=message):
        log_agent_event(event, logger)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    html = re.sub(r"^```(?:html)?\s*", "", response_text.strip())
    html = re.sub(r"\s*```$", "", html).strip()
    logger.info(f"WebpageDesignerAgent: {log_prefix} → {len(html)} chars")
    return html


async def run_webpage_design(
    request: WebpageRequest,
    reference_parts: list[types.Part] | None = None,
) -> WebpageResult:
    html = await _run_agent(_build_prompt(request), "initial design", reference_parts)
    return WebpageResult(html=html)


async def run_webpage_revision(
    current_html: str,
    issues: list[str],
    request: WebpageRequest,
    reference_parts: list[types.Part] | None = None,
) -> WebpageResult:
    """Re-run the designer with reviewer feedback. Reference parts re-sent so the model keeps the visual constraint."""
    issue_list = "\n".join(f"- {issue}" for issue in issues)
    prompt = (
        f"## Product Idea\n{request.idea}\n\n"
        f"You previously generated the HTML below. A reviewer has requested the following changes:\n\n"
        f"{issue_list}\n\n"
        f"Original user preferences: {request.text_preferences or 'None'}\n\n"
        f"Revise the HTML to address ALL of the issues above. "
        f"Return ONLY the corrected HTML file with the design plan comment at the top.\n\n"
        f"## Current HTML\n{current_html}"
    )
    html = await _run_agent(prompt, f"revision ({len(issues)} issues)", reference_parts)
    return WebpageResult(html=html)
