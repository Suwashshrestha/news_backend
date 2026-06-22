from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    slug: str
    color: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    color: Optional[str] = None
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


# ── Article ───────────────────────────────────────────────────────────────────

class ArticleOut(BaseModel):
    """
    image_path is the relative file path returned by the API.
    Frontend can build the full URL as: <base_url>/<image_path>
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: Optional[str]
    content: str
    image_path: Optional[str]        # e.g. "media/images/abc123.jpg"
    author_name: str
    views: int
    is_breaking_news: bool
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    category_id: Optional[int]
    category: Optional[CategoryOut]


class ArticleUpdate(BaseModel):
    """Used for PATCH – all fields optional (files handled separately via Form)."""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    author_name: Optional[str] = None
    is_breaking_news: Optional[bool] = None
    category_id: Optional[int] = None


# ── Video ─────────────────────────────────────────────────────────────────────

class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    video_path: Optional[str]        # e.g. "media/videos/abc123.mp4"
    youtube_id: Optional[str]        # optional YouTube embed ID
    thumbnail_path: Optional[str]    # e.g. "media/thumbnails/abc123.jpg"
    published_at: datetime
    created_at: datetime


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    youtube_id: Optional[str] = None


# ── Contact ───────────────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    is_read: bool
    submitted_at: datetime


# ── Advertisement ─────────────────────────────────────────────────────────────

class AdvertisementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image_path: Optional[str]
    redirect_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdvertisementUpdate(BaseModel):
    redirect_url: Optional[str] = None
    is_active: Optional[bool] = None


    # -------------------Gallery---------------------
class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    tags: Optional[str]
    description: Optional[str]
    image_path: str
    published_at: datetime
    created_at: datetime
    @field_serializer("image_path")
    def serialize_image_path(self, value: str):
        path = value.replace("\\", "/")
        return f"http://localhost:8000/{path}"


class PhotoUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None