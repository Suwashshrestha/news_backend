from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.crud import user as crud_user
from app.routers import ads, auth, categories, contact, news, uploads, videos,gallery

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploaded media ────────────────────────────────────
# Files saved as "media/images/abc.jpg" are served at GET /media/images/abc.jpg
media_dir = Path(settings.MEDIA_ROOT)
media_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.MEDIA_URL, StaticFiles(directory=str(media_dir)), name="media")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(news.router)
app.include_router(videos.router)
app.include_router(categories.router)
app.include_router(contact.router)
app.include_router(ads.router)
app.include_router(uploads.router)
app.include_router(gallery.router)


# ── Startup: seed default admin if not present ────────────────────────────────
@app.on_event("startup")
async def create_default_admin() -> None:
    async with AsyncSessionLocal() as db:
        existing = await crud_user.get_user_by_email(db, settings.ADMIN_EMAIL)
        if not existing:
            await crud_user.create_user(
                db,
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_admin=True,
            )


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME}