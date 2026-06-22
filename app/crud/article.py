from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Article
from app.core.storage import delete_file


# ── Read ──────────────────────────────────────────────────────────────────────

async def get_article(db: AsyncSession, article_id: int) -> Article | None:
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.category))
        .where(Article.id == article_id)
    )
    return result.scalar_one_or_none()


async def get_articles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    breaking_only: bool = False,
) -> list[Article]:
    q = select(Article).options(selectinload(Article.category))
    if category_id:
        q = q.where(Article.category_id == category_id)
    if breaking_only:
        q = q.where(Article.is_breaking_news == True)
    q = q.order_by(Article.published_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_trending_articles(
    db: AsyncSession,
    limit: int = 10,
) -> list[Article]:
    """Return articles ordered by view count (most viewed first)."""
    q = (
        select(Article)
        .options(selectinload(Article.category))
        .order_by(Article.views.desc(), Article.published_at.desc())
        .limit(limit)
    )
    result = await db.execute(q)
    return list(result.scalars().all())

# ── Create ────────────────────────────────────────────────────────────────────

async def create_article(
    db: AsyncSession,
    *,
    title: str,
    content: str,
    author_name: str,
    summary: str | None = None,
    image_path: str | None = None,
    category_id: int | None = None,
    is_breaking_news: bool = False,
) -> Article:
    article = Article(
        title=title,
        content=content,
        author_name=author_name,
        summary=summary,
        image_path=image_path,
        category_id=category_id,
        is_breaking_news=is_breaking_news,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    
    # Re-fetch with relationship to avoid lazy-loading error in FastAPI serialization
    return await get_article(db, article.id)


# ── Update ────────────────────────────────────────────────────────────────────

async def update_article(
    db: AsyncSession,
    article: Article,
    updates: dict,
    new_image_path: str | None = None,
) -> Article:
    if new_image_path:
        delete_file(article.image_path)   # remove old file
        updates["image_path"] = new_image_path

    for field, value in updates.items():
        if value is not None:
            setattr(article, field, value)

    await db.commit()
    await db.refresh(article)
    
    # Re-fetch with relationship to avoid lazy-loading error
    return await get_article(db, article.id)


# ── Delete ────────────────────────────────────────────────────────────────────

async def delete_article(db: AsyncSession, article: Article) -> None:
    delete_file(article.image_path)
    await db.delete(article)
    await db.commit()


# ── Increment views ───────────────────────────────────────────────────────────

async def increment_views(db: AsyncSession, article_id: int) -> None:
    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(views=Article.views + 1)
    )
    await db.commit()