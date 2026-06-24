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
@router.post("/", response_model=PhotoOut)
async def create_photo(
    title: str = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None),
    sub_images: list[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
):
    image_path = await save_image(image) if image else None

    sub_image_paths = []

    for img in sub_images:
        path = await save_image(img)

        if path:
            sub_image_paths.append(
                path.replace("\\", "/")
            )

    photo = Photo(
        title=title,
        description=description,
        image_path=image_path,
        sub_images=sub_image_paths,
    )

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
    sub_images: list[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(Photo).where(Photo.id == photo_id)
    )

    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )

    if title is not None:
        photo.title = title

    if description is not None:
        photo.description = description

    if tag is not None:
        photo.tag = tag

    if image:
        photo.image_path = await save_image(image)

    if sub_images:
        paths = []

        for img in sub_images:
            path = await save_image(img)
            paths.append(path.replace("\\", "/"))

        photo.sub_images = paths

    await db.commit()
    await db.refresh(photo)

    return photo