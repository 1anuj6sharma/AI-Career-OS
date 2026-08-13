from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.offers.repository import OfferRepository
from app.modules.offers.service import OfferService
from app.modules.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_offer_service(db: Session = Depends(get_db)) -> OfferService:
    repo = OfferRepository(db)
    return OfferService(repo, llm_service)
