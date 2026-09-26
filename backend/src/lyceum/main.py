from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lyceum.auth.api import router as auth_router
from lyceum.auth.exception_handlers import register_auth_exception_handlers
from lyceum.chapters.api import router as chapter_router
from lyceum.core.config import get_settings
from lyceum.courses.api import router as course_router
from lyceum.shared.exception_handlers import register_shared_exception_handlers
from lyceum.users.api import router as user_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(course_router)
app.include_router(chapter_router)

register_auth_exception_handlers(app)
register_shared_exception_handlers(app)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
