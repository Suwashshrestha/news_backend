"""
All SQLAlchemy ORM models.
- Article.image_path   → uploaded image stored in media/images/
- Video.video_path     → uploaded video stored in media/videos/
- Video.thumbnail_path → uploaded thumbnail stored in media/thumbnails/
"""

from datetime import datetime, timezone

from sqlalchemy import JSON

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.core.config import settings


# ── User (Admin / Editor) ─────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ── Category ──────────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Hex code or CSS color
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    articles: Mapped[list["Article"]] = relationship("Article", back_populates="category")


# ── Article ───────────────────────────────────────────────────────────────────

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Uploaded image file path (e.g. "media/images/abc123.jpg")
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sub_images: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    author_name: Mapped[str] = mapped_column(String(150), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_breaking_news: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped["Category | None"] = relationship("Category", back_populates="articles")


# ── Video ─────────────────────────────────────────────────────────────────────

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Uploaded video file path (e.g. "media/videos/abc123.mp4")
    video_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # YouTube ID kept for optional embed support (e.g. "dQw4w9WgXcQ")
    youtube_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Uploaded thumbnail image path (e.g. "media/thumbnails/abc123.jpg")
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ── Advertisement ─────────────────────────────────────────────────────────────

class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    redirect_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )


# ── Contact Submission ────────────────────────────────────────────────────────

class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

# ── Photo Gallery ────────────────────────────────────────────────────────────

class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(300), nullable=False)

    tags: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )  # comma separated tags

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Uploaded image path
    image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    sub_images: Mapped[list[str]] = mapped_column(
     JSON,
    default=list,
    nullable=False)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
