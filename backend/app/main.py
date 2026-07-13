from fastapi import FastAPI
from sqlalchemy import text

from app.core.logging import logger
from app.core.logging import setup_logging
from app.api.v1.api import api_router

setup_logging()
from app.core.security import (
    hash_password,
    verify_password,
)

from app.core.config import settings
from app.database.session import SessionLocal

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

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


@app.get("/database-test")
def database_test():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "database": "Connected Successfully"
        }

    finally:
        db.close()
        
from app.core.security import (
    hash_password,
    verify_password,
)      
        

@app.get("/security-test")
def security_test():
    password = "Hello123"

    hashed = hash_password(password)
    verified = verify_password(password, hashed)

    return {
        "password": password,
        "hashed": hashed,
        "verified": verified
    }


app.include_router(
    api_router,
    prefix="/api/v1",
)
