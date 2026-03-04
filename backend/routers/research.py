from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.research import IdeaRequest, ResearchResult
from backend.agents.research_agent import run_research
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.models.event_log import EventType
from backend.services.event_service import log_event, log_idea_analytics
from backend.tools.doc_parser import extract_text, MAX_FILE_SIZE, ALLOWED_TEXT_EXTENSIONS
from backend.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResult)
async def research_idea(
    request: IdeaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Research request from {current_user.username}: '{request.idea[:60]}'")
    try:
        result = await run_research(request)
        event = await log_event(
            db, EventType.RESEARCH_QUERY,
            user_id=current_user.id,
            metadata={"idea_preview": request.idea[:100]},
        )
        await log_idea_analytics(
            db,
            user_id=current_user.id,
            idea_text=request.idea,
            result=result,
            event_log_id=event.id if event else None,
        )
        return result
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Research agent error")


@router.post("/upload", response_model=ResearchResult)
async def research_with_document(
    idea: str = Form(...),
    reference_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research endpoint that accepts an optional document (.txt / .md / .pdf) to augment the idea."""
    idea_text = idea

    if file and file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_TEXT_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only .txt, .md, .pdf files are supported")
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 2MB limit")
        doc_text = await extract_text(file_bytes, file.filename)
        idea_text = f"{idea}\n\n## Additional Context from Uploaded Document\n{doc_text}"
        logger.info(f"Research upload: appended {len(doc_text)} chars from '{file.filename}'")

    request = IdeaRequest(idea=idea_text, reference_url=reference_url)
    logger.info(f"Research upload request from {current_user.username}: '{idea[:60]}'")
    try:
        result = await run_research(request)
        event = await log_event(
            db, EventType.RESEARCH_QUERY,
            user_id=current_user.id,
            metadata={"idea_preview": idea[:100], "has_document": file is not None},
        )
        await log_idea_analytics(
            db,
            user_id=current_user.id,
            idea_text=idea_text,
            result=result,
            event_log_id=event.id if event else None,
        )
        return result
    except Exception as e:
        logger.error(f"Research agent (upload) failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Research agent error")
