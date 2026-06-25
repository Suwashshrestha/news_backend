"""
News / Articles router.
Image is accepted as a multipart file upload (not a URL).
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.core.storage import save_image
from app.crud import article as crud_article
from app.db.session import get_db
from app.schemas.schemas import ArticleOut, ArticleUpdate

router = APIRouter(prefix="/news", tags=["news"])


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("/", response_model=list[ArticleOut])
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None),
    breaking: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    return await crud_article.get_articles(
        db, skip=skip, limit=limit, category_id=category_id, breaking_only=breaking
    )


@router.get("/trending", response_model=list[ArticleOut])
async def get_trending(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return articles sorted by view count (most viewed first)."""
    return await crud_article.get_trending_articles(db, limit=limit)


@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    article = await crud_article.get_article(db, article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await crud_article.increment_views(db, article_id)

    article = await crud_article.get_article(db, article_id)

    return article


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("/", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    title: str = Form(...),
    content: str = Form(...),
    author_name: str = Form(...),
    summary: str | None = Form(None),
    category_id: int | None = Form(None),
    is_breaking_news: bool = Form(False),
    # ✅ Image uploaded as a file, not a URL
    image: UploadFile | None = File(None),
    sub_images: list[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    image_path = await save_image(image) if image else None

    sub_image_paths = []

    for img in sub_images:
     path = await save_image(img)
     sub_image_paths.append(path.replace("\\", "/"))
    
    return await crud_article.create_article(
        db,
        title=title,
        content=content,
        author_name=author_name,
        summary=summary,
        image_path=image_path,
        sub_images=sub_image_paths,
        category_id=category_id,
        is_breaking_news=is_breaking_news,
    )


@router.patch("/{article_id}", response_model=ArticleOut)
async def update_article(
    article_id: int,
    title: str | None = Form(None),
    summary: str | None = Form(None),
    content: str | None = Form(None),
    author_name: str | None = Form(None),
    is_breaking_news: bool | None = Form(None),
    category_id: int | None = Form(None),
    # ✅ New image can be re-uploaded; old file is deleted automatically
    image: UploadFile | None = File(None),
    sub_images: list[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    article = await crud_article.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    new_image_path = await save_image(image) if image else None
    sub_image_paths = []

    if sub_images:
     for img in sub_images:
        path = await save_image(img)

        if path:
            sub_image_paths.append(
                path.replace("\\", "/")
            )
    updates = {
        k: v for k, v in {
            "title": title,
            "summary": summary,
            "content": content,
            "author_name": author_name,
            "is_breaking_news": is_breaking_news,
            "category_id": category_id,
            "sub_images": sub_image_paths if sub_image_paths else None
        }.items() if v is not None
    }
    return await crud_article.update_article(db, article, updates, new_image_path=new_image_path,sub_images=sub_image_paths, )


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    article = await crud_article.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await crud_article.delete_article(db, article)