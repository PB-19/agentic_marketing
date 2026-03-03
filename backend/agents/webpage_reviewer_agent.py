import json
import re
import uuid
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from backend.schemas.webpage import WebpageRequest, WebpageResult, DeployResult
from backend.agents.webpage_designer_agent import run_webpage_revision
from backend.tools.gcs_tools import gcs_upload, tinyurl_shorten
from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)

_MAX_ITERATIONS = 3

_INSTRUCTION = """You are a QA-focused frontend reviewer evaluating a static HTML landing page.

Review the HTML against the checklist below and the user's original preferences (if any).
You are on a specific iteration — calibrate accordingly:
  - Iteration 1: thorough — list ALL issues
  - Iteration 2: verify fixes — note any issues that were NOT addressed from prior feedback
  - Iteration 3: final — note remaining issues but do not request further changes (iteration limit)

## Review Checklist
- Visual/content alignment with reference URL or user preferences (if provided)
- Responsive layout: CSS Grid/Flexbox, no fixed pixel widths that break on mobile
- No broken inline styles or obviously missing sections
- Required sections present: Hero, Features/Benefits, CTA, Footer
- Readable typography and sufficient color contrast
- No external CDN dependencies required for the page to render

Respond ONLY with valid JSON — no markdown, no explanation:
{
  "status": "approved" | "changes_requested",
  "issues": ["issue 1", "issue 2"],
  "notes": "string or null"
}

If on iteration 3, always set status to "approved" and list any remaining issues in "notes"."""


@dataclass
class _ReviewVerdict:
    status: str          # "approved" | "changes_requested"
    issues: list[str]
    notes: str | None


_session_service = InMemorySessionService()

_reviewer_agent = Agent(
    name="WebpageReviewerAgent",
    model=settings.GOOGLE_GENAI_MODEL,
    instruction=_INSTRUCTION,
    tools=[],  # Pure LLM judge — no tools; GCS/TinyURL handled by Python orchestrator
)


def _build_review_prompt(html: str, request: WebpageRequest, iteration: int) -> str:
    lines = [f"## Review Request — Iteration {iteration} of {_MAX_ITERATIONS}"]

    if request.reference_url:
        lines.append(f"**Reference URL**: {request.reference_url}")
    if request.text_preferences:
        lines.append(f"**User preferences**: {request.text_preferences}")

    lines += ["", "## HTML to Review", "```html", html, "```"]
    return "\n".join(lines)


async def _run_review(html: str, request: WebpageRequest, iteration: int) -> _ReviewVerdict:
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name="agentic_marketing",
        user_id="system",
        session_id=session_id,
    )
    runner = Runner(
        agent=_reviewer_agent,
        app_name="agentic_marketing",
        session_service=_session_service,
    )

    prompt = _build_review_prompt(html, request, iteration)
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    response_text = ""

    async for event in runner.run_async(user_id="system", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    clean = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
    data = json.loads(clean)
    return _ReviewVerdict(
        status=data.get("status", "approved"),
        issues=data.get("issues", []),
        notes=data.get("notes"),
    )


_LOCAL_PAGES_DIR = Path(__file__).resolve().parents[1] / "storage" / "pages"


def _save_local(html: str) -> None:
    _LOCAL_PAGES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
    path = _LOCAL_PAGES_DIR / filename
    path.write_text(html, encoding="utf-8")
    logger.info(f"Saved finalized HTML locally: {path}")


async def run_design_review_loop(request: WebpageRequest) -> DeployResult:
    """
    Orchestrates the designer → reviewer loop with a hard cap of _MAX_ITERATIONS (3).
    The loop is controlled entirely in Python — the agents never drive iteration themselves.
    """
    from backend.agents.webpage_designer_agent import run_webpage_design

    # Initial design pass
    logger.info("Design-review loop: starting initial design")
    result: WebpageResult = await run_webpage_design(request)
    html = result.html

    for iteration in range(1, _MAX_ITERATIONS + 1):
        logger.info(f"Design-review loop: reviewer iteration {iteration}/{_MAX_ITERATIONS}")
        verdict = await _run_review(html, request, iteration)

        approved = verdict.status == "approved" or iteration == _MAX_ITERATIONS

        if verdict.issues:
            logger.info(f"Iteration {iteration} issues: {verdict.issues}")
        else:
            logger.info(f"Iteration {iteration}: no issues found")

        if approved:
            status_label = "approved" if verdict.status == "approved" else "approved (iteration limit reached)"
            logger.info(f"Design-review loop: {status_label} at iteration {iteration} — deploying")
            _save_local(html)
            gcs_url = await gcs_upload(html)
            tiny_url = await tinyurl_shorten(gcs_url)
            return DeployResult(
                html=html,
                gcs_url=gcs_url,
                tiny_url=tiny_url,
                iteration=iteration,
                notes=verdict.notes,
            )

        # Revision needed — send feedback back to designer
        logger.info(f"Design-review loop: requesting revision after iteration {iteration}")
        revised: WebpageResult = await run_webpage_revision(html, verdict.issues, request)
        html = revised.html

    # Should never reach here given the approved check above, but guard anyway
    raise RuntimeError("Design-review loop exited without deploying")  # pragma: no cover
