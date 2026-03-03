import asyncio
import uuid
import httpx
from google.cloud import storage
from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


async def gcs_upload(html: str) -> str:
    """Upload HTML string to GCS and return the public URL."""
    object_name = f"pages/{uuid.uuid4()}/index.html"

    def _upload() -> str:
        client = storage.Client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(html.encode("utf-8"), content_type="text/html")
        return blob.public_url

    url = await asyncio.to_thread(_upload)
    logger.info(f"Uploaded page to GCS: {url}")
    return url


async def tinyurl_shorten(url: str) -> str:
    """Shorten a URL using the TinyURL v1 API (Bearer token auth)."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://api.tinyurl.com/create",
            headers={
                "Authorization": f"Bearer {settings.TINYURL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"url": url, "domain": "tinyurl.com"},
        )
        resp.raise_for_status()
        short = resp.json()["data"]["tiny_url"]
    logger.info(f"TinyURL: {short}")
    return short
