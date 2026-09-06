from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.controllers.interviews.repository import InterviewRepository
from app.controllers.interviews.service import InterviewService
from app.controllers.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_interview_service(db: Session = Depends(get_db)) -> InterviewService:
    repo = InterviewRepository(db)
    return InterviewService(repo, llm_service)
