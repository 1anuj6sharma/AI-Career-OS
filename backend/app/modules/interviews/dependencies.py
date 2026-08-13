from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.interviews.repository import InterviewRepository
from app.modules.interviews.service import InterviewService
from app.modules.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_interview_service(db: Session = Depends(get_db)) -> InterviewService:
    repo = InterviewRepository(db)
    return InterviewService(repo, llm_service)
