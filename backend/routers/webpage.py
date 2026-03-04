from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from google.genai import types
from backend.database import get_db
from backend.schemas.webpage import WebpageRequest, WebpageResult, DeployResult
from backend.schemas.research import ResearchResult
from backend.agents.webpage_designer_agent import run_webpage_design
from backend.agents.webpage_reviewer_agent import run_design_review_loop
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.event_log import EventType
from backend.services.event_service import log_event
from backend.tools.doc_parser import extract_design_images, ALLOWED_DESIGN_EXTENSIONS, MAX_FILE_SIZE
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webpage", tags=["webpage"])


@router.post("/design", response_model=WebpageResult)
async def design_webpage(
    request: WebpageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Webpage design request from {current_user.username}")
    try:
        result = await run_webpage_design(request)
        await log_event(
            db, EventType.DESIGN_REQUEST,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100]},
        )
        return result
    except Exception as e:
        logger.error(f"WebpageDesignerAgent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webpage designer agent error")


@router.post("/design-and-deploy", response_model=DeployResult)
async def design_and_deploy(
    request: WebpageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full pipeline: design → review loop (max 3 iterations) → GCS deploy → TinyURL."""
    logger.info(f"Design-and-deploy request from {current_user.username}")
    try:
        result = await run_design_review_loop(request)
        await log_event(
            db, EventType.DEPLOY_REQUEST,
            user_id=current_user.id,
            metadata={
                "idea_preview": request.idea[:100],
                "tiny_url": result.tiny_url,
                "iteration": result.iteration,
            },
        )
        return result
    except Exception as e:
        logger.error(f"Design-review loop failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Design-and-deploy pipeline error")


@router.post("/design-and-deploy-with-ref", response_model=DeployResult)
async def design_and_deploy_with_ref(
    idea: str = Form(...),
    research: str = Form(...),  # JSON-serialised ResearchResult
    reference_url: str | None = Form(None),
    text_preferences: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Design + deploy with an optional visual reference (image or PDF upload, or URL).
    The agent treats the reference as a primary design constraint, not just inspiration."""
    research_data = ResearchResult.model_validate_json(research)
    request = WebpageRequest(
        idea=idea,
        research=research_data,
        reference_url=reference_url,
        text_preferences=text_preferences,
    )

    reference_parts: list[types.Part] | None = None
    if file and file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_DESIGN_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only JPG, PNG, WEBP, or PDF files are supported as design references",
            )
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 2MB limit")
        images = await extract_design_images(file_bytes, file.filename)
        reference_parts = [
            types.Part(inline_data=types.Blob(mime_type=mime, data=img_bytes))
            for img_bytes, mime in images
        ]
        logger.info(f"Design-with-ref: {len(reference_parts)} reference image part(s) from '{file.filename}'")

    logger.info(f"Design-and-deploy-with-ref request from {current_user.username}")
    try:
        result = await run_design_review_loop(request, reference_parts)
        await log_event(
            db, EventType.DEPLOY_REQUEST,
            user_id=current_user.id,
            metadata={
                "idea_preview": idea[:100],
                "tiny_url": result.tiny_url,
                "iteration": result.iteration,
                "has_reference": file is not None or reference_url is not None,
            },
        )
        return result
    except Exception as e:
        logger.error(f"Design-review loop (with-ref) failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Design-and-deploy pipeline error")
