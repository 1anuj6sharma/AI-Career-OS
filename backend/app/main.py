from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import logger, setup_logging
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exception import register_exception_handlers
from app.database.base import Base
from app.database.session import engine

# Import all models to ensure they are registered with Base metadata
import app.modules.auth.models
import app.modules.profile.models
import app.modules.jobs.models
import app.modules.resumes.models
import app.modules.interviews.models
import app.modules.career.models
import app.modules.learning.models
import app.modules.brand.models
import app.modules.opportunities.models
import app.modules.network.models
import app.modules.offers.models
import app.modules.master_orchestrator.models
import app.modules.integrations.models
import app.modules.dashboard.models

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL Database tables verified & initialized.")
    except Exception as e:
        logger.warn(f"Database initialization note: {e}")

if settings.BACKEND_CORS_ORIGINS:
    origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)

@app.get("/")
def root():
    logger.info("Root endpoint accessed.")
    return {
        "message": "AI Career Operating System Backend Running 🚀"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "debug": settings.DEBUG,
    }

app.include_router(
    api_router,
    prefix="/api/v1",
)
