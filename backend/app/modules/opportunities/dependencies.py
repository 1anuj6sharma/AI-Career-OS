from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.opportunities.repository import OpportunityRepository
from app.modules.opportunities.service import OpportunityService
from app.modules.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_opportunity_service(db: Session = Depends(get_db)) -> OpportunityService:
    repo = OpportunityRepository(db)
    return OpportunityService(repo, llm_service)
