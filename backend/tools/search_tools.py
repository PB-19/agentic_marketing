import re
import httpx
from backend.logger import get_logger

logger = get_logger(__name__)


async def url_fetch(url: str) -> str:
    """Fetches and returns cleaned text content from a URL. Strips HTML tags."""
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        logger.info(f"Fetching URL: {url}")
        resp = await client.get(url)
        resp.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        logger.info(f"Fetched {len(text)} chars from {url}")
        # Truncated to avoid token explosion
        return text[:5000]
