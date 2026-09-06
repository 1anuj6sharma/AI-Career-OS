from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.controllers.career.repository import CareerRepository
from app.controllers.career.service import CareerService
from app.controllers.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_career_service(db: Session = Depends(get_db)) -> CareerService:
    repo = CareerRepository(db)
    return CareerService(repo, llm_service)
