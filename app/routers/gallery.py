from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.core.storage import save_image, delete_file
from app.db.session import get_db
from app.models.models import Photo
from app.schemas.schemas import PhotoOut
from sqlalchemy import select

router = APIRouter(prefix="/photos", tags=["photos"])

@router .get("/", response_model=list[PhotoOut])
async def list_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
 result = await db.execute(select(Photo) .offset(skip).limit(limit).order_by(Photo.created_at.desc()))
 return list(result.scalars().all())

@router .delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    delete_file(photo.image_path)
    await db.delete(photo)
    await db.commit()

@router.get ("/{photo_id}", response_model=PhotoOut)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router .post("/", response_model=PhotoOut)
async def create_photo(
    image: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    tag: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    image_path = await save_image(image)
    photo = Photo(image_path=image_path, title=title, description=description)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo

@router.patch("/{photo_id}", response_model=PhotoOut)
async def update_photo(
    photo_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    tag: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if image:
        new_image_path = await save_image(image)
        delete_file(photo.image_path)
        photo.image_path = new_image_path

    updates = {k: v for k, v in {"title": title, "description": description, "tag": tag}.items() if v is not None}
    for field, value in updates.items():
        setattr(photo, field, value)

    await db.commit()
    await db.refresh(photo)
    return photo  
