"""
File upload utilities.
Uploaded files are saved under the `media/` directory:
  media/images/<uuid>.<ext>
  media/videos/<uuid>.<ext>
  media/thumbnails/<uuid>.<ext>
"""

import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

from app.core.config import settings

MEDIA_ROOT = Path(settings.MEDIA_ROOT)
IMAGE_DIR = MEDIA_ROOT / "images"
VIDEO_DIR = MEDIA_ROOT / "videos"
THUMBNAIL_DIR = MEDIA_ROOT / "thumbnails"

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg", "video/quicktime"}

MAX_IMAGE_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_VIDEO_BYTES = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024


async def _save(
    file: UploadFile,
    dest_dir: Path,
    allowed_types: set[str],
    max_bytes: int,
) -> str:
    """Validate, stream-save an upload, and return the relative path."""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {allowed_types}",
        )

    dest_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "file").suffix.lower() or ".bin"
    filename = f"{uuid.uuid4().hex}{suffix}"
    full_path = dest_dir / filename

    written = 0
    async with aiofiles.open(full_path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)  # 1 MB chunks
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                await file.close()
                full_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds maximum allowed size of {max_bytes // (1024*1024)} MB",
                )
            await out.write(chunk)

    # Return a URL-ready relative path, e.g. "media/images/abc.jpg"
    return str(full_path)


async def save_image(file: UploadFile) -> str:
    """Save an image upload and return its relative path."""
    return await _save(file, IMAGE_DIR, ALLOWED_IMAGE_TYPES, MAX_IMAGE_BYTES)


async def save_video(file: UploadFile) -> str:
    """Save a video upload and return its relative path."""
    return await _save(file, VIDEO_DIR, ALLOWED_VIDEO_TYPES, MAX_VIDEO_BYTES)


async def save_thumbnail(file: UploadFile) -> str:
    """Save a thumbnail image and return its relative path."""
    return await _save(file, THUMBNAIL_DIR, ALLOWED_IMAGE_TYPES, MAX_IMAGE_BYTES)


def delete_file(relative_path: str | None) -> None:
    """Delete a previously saved media file (best-effort, no error on missing)."""
    if relative_path:
        Path(relative_path).unlink(missing_ok=True)