from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.deps import get_current_admin
from app.core.storage import save_image, delete_file
from app.db.session import get_db
from app.models.models import Advertisement
from app.schemas.schemas import AdvertisementOut

router = APIRouter(prefix="/ads", tags=["ads"])


@router.get("/", response_model=List[AdvertisementOut])
async def list_active_ads(db: AsyncSession = Depends(get_db)):
    """Fetch all active advertisements."""
    result = await db.execute(
        select(Advertisement).where(Advertisement.is_active == True)
    )
    return list(result.scalars().all())


@router.get("/all", response_model=List[AdvertisementOut])
async def list_all_ads(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    """Fetch all ads (including inactive) - Admin only."""
    result = await db.execute(select(Advertisement))
    return list(result.scalars().all())


@router.patch("/{slug}", response_model=AdvertisementOut)
async def update_ad(
    slug: str,
    redirect_url: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Update or create an advertisement slot by slug."""
    result = await db.execute(
        select(Advertisement).where(Advertisement.slug == slug)
    )
    ad = result.scalar_one_or_none()

    if not ad:
        # If it doesn't exist, we create it (auto-provisioning slots)
        ad = Advertisement(slug=slug)
        db.add(ad)

    if redirect_url is not None:
        ad.redirect_url = redirect_url
    if is_active is not None:
        ad.is_active = is_active
    
    if image:
        # If updating image, delete old one if exists
        if ad.image_path:
            delete_file(ad.image_path)
        ad.image_path = await save_image(image)

    await db.commit()
    await db.refresh(ad)
    return ad


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    slug: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Delete an ad slot."""
    result = await db.execute(
        select(Advertisement).where(Advertisement.slug == slug)
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad slot not found")
    
    if ad.image_path:
        delete_file(ad.image_path)
    
    await db.delete(ad)
    await db.commit()
