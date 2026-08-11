from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import logger, setup_logging
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exception import register_exception_handlers

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

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
