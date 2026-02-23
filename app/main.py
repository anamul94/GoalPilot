from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
