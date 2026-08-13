from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.service import JobService


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    repo = JobRepository(db)
    return JobService(repo)
