from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import logger, setup_logging
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exception import register_exception_handlers
from app.database.base import Base
from app.database.session import engine

# Import all models to ensure they are registered with Base metadata
import app.models.auth
import app.models.profile
import app.models.jobs
import app.models.resumes
import app.models.interviews
import app.models.career
import app.models.learning
import app.models.brand
import app.models.opportunities
import app.models.network
import app.models.offers
import app.models.master_orchestrator
import app.models.integrations
import app.models.dashboard
import app.models.ai_coach

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
