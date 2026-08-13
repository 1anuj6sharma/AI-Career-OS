from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.learning.repository import LearningRepository
from app.modules.learning.service import LearningService
from app.modules.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_learning_service(db: Session = Depends(get_db)) -> LearningService:
    repo = LearningRepository(db)
    return LearningService(repo, llm_service)
