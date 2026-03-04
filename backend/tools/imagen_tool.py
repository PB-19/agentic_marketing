import asyncio
import uuid
from pathlib import Path

from PIL import Image
from google.cloud import storage

from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)

_TMP_DIR = Path(__file__).resolve().parents[1] / "storage" / "instagram_tmp"


async def generate_image(prompt: str) -> str:
    """Generate an Instagram-ready image from a text prompt using Imagen via Vertex AI.
    Uploads the JPEG to GCS and returns the public GCS URL.
    The agent MUST call this tool — do not fabricate the returned URL."""

    def _generate() -> str:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel

        _TMP_DIR.mkdir(parents=True, exist_ok=True)
        file_id = uuid.uuid4().hex

        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
        )
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        images = model.generate_images(prompt=prompt, number_of_images=1)

        # Save as PNG, convert to JPEG (Instagram requires JPEG)
        png_path = _TMP_DIR / f"{file_id}_tmp.png"
        jpg_path = _TMP_DIR / f"{file_id}.jpg"

        images[0].save(location=str(png_path), include_generation_parameters=False)
        img = Image.open(png_path).convert("RGB")
        img.save(str(jpg_path), "JPEG", quality=95)
        png_path.unlink(missing_ok=True)

        # Upload to GCS
        object_name = f"instagram/{file_id}.jpg"
        gcs_client = storage.Client()
        bucket = gcs_client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_filename(str(jpg_path), content_type="image/jpeg")
        public_url = blob.public_url

        jpg_path.unlink(missing_ok=True)
        logger.info(f"Imagen: uploaded to GCS → {public_url}")
        return public_url

    return await asyncio.to_thread(_generate)
