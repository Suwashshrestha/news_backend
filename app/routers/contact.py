from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models.models import ContactSubmission
from app.schemas.schemas import ContactCreate, ContactOut

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
async def submit_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    submission = ContactSubmission(**payload.model_dump())
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


# ── Admin only ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ContactOut])
async def list_submissions(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    q = select(ContactSubmission).order_by(ContactSubmission.submitted_at.desc())
    if unread_only:
        q = q.where(ContactSubmission.is_read == False)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.patch("/{submission_id}/read", response_model=ContactOut)
async def mark_as_read(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == submission_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub.is_read = True
    await db.commit()
    await db.refresh(sub)
    return sub