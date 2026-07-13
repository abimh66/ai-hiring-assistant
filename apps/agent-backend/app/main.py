from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.applications.routes import applications_router, project_applications_router
from app.modules.auth.routes import router as auth_router
from app.modules.candidates.routes import router as candidates_router
from app.modules.hiring_projects.routes import router as hiring_projects_router
from app.modules.storage.client import ensure_bucket


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_bucket()
    yield


app = FastAPI(title="AI Hiring Assistant — agent-backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(hiring_projects_router)
app.include_router(project_applications_router)
app.include_router(applications_router)
app.include_router(candidates_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
