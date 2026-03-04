import asyncio
import tempfile
import uuid

import httpx

from backend.logger import get_logger

logger = get_logger(__name__)


async def post_to_instagram(username: str, password: str, image_url: str, caption: str) -> dict:
    """Post a single image to Instagram via instagrapi.

    Downloads the image from its GCS public URL to a temp file, posts it, then cleans up.
    Credentials are used in-memory only — never logged, stored, or forwarded.
    Returns dict with media_id and code on success.
    Raises RuntimeError on failure.
    """
    # Download image from GCS to a local temp file (instagrapi needs a local path)
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
        image_bytes = resp.content

    def _post(tmp_path: str) -> dict:
        from pathlib import Path
        from instagrapi import Client
        from instagrapi.exceptions import LoginRequired, RateLimitError, ChallengeRequired

        cl = Client()
        cl.delay_range = [10, 20]

        try:
            cl.login(username, password)
        except ChallengeRequired as e:
            raise RuntimeError("Instagram challenge required — log in manually once to resolve.") from e
        except LoginRequired as e:
            raise RuntimeError("Instagram login failed — check credentials.") from e

        try:
            media = cl.photo_upload(Path(tmp_path), caption)
            logger.info(f"Instagram: posted media_id={media.id}")
            return {"media_id": str(media.id), "code": media.code}
        except RateLimitError as e:
            raise RuntimeError("Instagram rate limit reached — try again later.") from e
        finally:
            try:
                cl.logout()
            except Exception:
                pass

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        result = await asyncio.to_thread(_post, tmp_path)
    finally:
        import os
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return result
