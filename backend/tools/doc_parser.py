import asyncio
from pathlib import Path

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_TEXT_EXTENSIONS = {".txt", ".md", ".pdf"}
ALLOWED_DESIGN_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}


async def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from .txt, .md, or .pdf files. Returns up to 8000 chars."""
    ext = Path(filename).suffix.lower()
    if ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="replace")[:8000]
    if ext == ".pdf":
        return await asyncio.to_thread(_pdf_to_text, file_bytes)
    raise ValueError(f"Unsupported file type: {ext}")


def _pdf_to_text(file_bytes: bytes) -> str:
    import fitz
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    return text[:8000]


async def extract_design_images(file_bytes: bytes, filename: str) -> list[tuple[bytes, str]]:
    """Return a list of (image_bytes, mime_type) for use as multimodal Parts.
    Images are returned as-is; PDFs are rendered (first 2 pages) to PNG."""
    ext = Path(filename).suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return [(file_bytes, "image/jpeg")]
    if ext == ".png":
        return [(file_bytes, "image/png")]
    if ext == ".webp":
        return [(file_bytes, "image/webp")]
    if ext == ".pdf":
        pages = await asyncio.to_thread(_pdf_to_images, file_bytes, 2)
        return [(p, "image/png") for p in pages]
    raise ValueError(f"Unsupported design reference type: {ext}")


def _pdf_to_images(file_bytes: bytes, max_pages: int) -> list[bytes]:
    import fitz
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    result = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        result.append(pix.tobytes("png"))
    return result
