"""
Videos router.
Both video and thumbnail are accepted as multipart file uploads.
youtube_id remains optional for YouTube embed support.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.core.storage import delete_file, save_thumbnail, save_video
from app.db.session import get_db
from app.models.models import Video
from app.schemas.schemas import VideoOut, VideoUpdate

router = APIRouter(prefix="/videos", tags=["videos"])


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("/", response_model=list[VideoOut])
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Video).order_by(Video.published_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{video_id}", response_model=VideoOut)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("/", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
async def create_video(
    title: str = Form(...),
    description: str | None = Form(None),
    youtube_id: str | None = Form(None),       # optional: YouTube embed ID
    # ✅ Video file uploaded directly
    video: UploadFile | None = File(None),
    # ✅ Thumbnail image uploaded directly
    thumbnail: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    if not video and not youtube_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either a video file upload or a youtube_id",
        )

    video_path = await save_video(video) if video else None
    thumbnail_path = await save_thumbnail(thumbnail) if thumbnail else None

    new_video = Video(
        title=title,
        description=description,
        youtube_id=youtube_id,
        video_path=video_path,
        thumbnail_path=thumbnail_path,
    )
    db.add(new_video)
    await db.commit()
    await db.refresh(new_video)
    return new_video


@router.patch("/{video_id}", response_model=VideoOut)
async def update_video(
    video_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    youtube_id: str | None = Form(None),
    # ✅ Re-upload to replace existing files; old files are deleted
    video: UploadFile | None = File(None),
    thumbnail: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    vid = result.scalar_one_or_none()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    if video:
        delete_file(vid.video_path)
        vid.video_path = await save_video(video)

    if thumbnail:
        delete_file(vid.thumbnail_path)
        vid.thumbnail_path = await save_thumbnail(thumbnail)

    if title is not None:
        vid.title = title
    if description is not None:
        vid.description = description
    if youtube_id is not None:
        vid.youtube_id = youtube_id

    await db.commit()
    await db.refresh(vid)
    return vid


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    vid = result.scalar_one_or_none()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    delete_file(vid.video_path)
    delete_file(vid.thumbnail_path)
    await db.delete(vid)
    await db.commit()