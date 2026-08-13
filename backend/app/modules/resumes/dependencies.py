from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.resumes.repository import ResumeRepository
from app.modules.resumes.service import ResumeService
from app.modules.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_resume_service(db: Session = Depends(get_db)) -> ResumeService:
    repo = ResumeRepository(db)
    return ResumeService(repo, llm_service)
