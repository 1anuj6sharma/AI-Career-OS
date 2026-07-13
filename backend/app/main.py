from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.database.session import SessionLocal

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} Backend Running 🚀"
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
        
from app.database.init_db import create_database        
@app.get("/init-db")
def initialize_database():
    create_database()

    return {
        "message": "Database initialized successfully"
    }
