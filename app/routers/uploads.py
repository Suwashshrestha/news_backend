"""
uploads.py – utility endpoint for upload configuration info.
Actual static file serving is configured in main.py via StaticFiles mount.
"""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/info")
async def upload_info():
    """Returns accepted file types, size limits, and where files are served."""
    base = settings.BASE_URL.rstrip("/")
    media = settings.MEDIA_URL.rstrip("/")
    return {
        "images": {
            "allowed_types": ["image/jpeg", "image/png", "image/webp", "image/gif"],
            "max_size_mb": settings.MAX_IMAGE_SIZE_MB,
            "served_at": f"{base}{media}/images/<filename>",
        },
        "videos": {
            "allowed_types": ["video/mp4", "video/webm", "video/ogg", "video/quicktime"],
            "max_size_mb": settings.MAX_VIDEO_SIZE_MB,
            "served_at": f"{base}{media}/videos/<filename>",
        },
        "thumbnails": {
            "allowed_types": ["image/jpeg", "image/png", "image/webp", "image/gif"],
            "max_size_mb": settings.MAX_IMAGE_SIZE_MB,
            "served_at": f"{base}{media}/thumbnails/<filename>",
        },
    }