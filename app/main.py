from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import get_settings
from app.routers import auth, categories, goals, milestones, tasks, checklists, analytics, notifications

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Goal Execution Platform API – Define goals, break into milestones & tasks, track progress automatically.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(static_path, "favicon.ico")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"detail": "Not Found"}


@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
async def apple_touch_icon():
    file_path = os.path.join(static_path, "apple-touch-icon.png")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"detail": "Not Found"}


# Register routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(goals.router)
app.include_router(milestones.router)
app.include_router(tasks.router)
app.include_router(checklists.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
