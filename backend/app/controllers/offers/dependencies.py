from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.controllers.offers.repository import OfferRepository
from app.controllers.offers.service import OfferService
from app.controllers.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_offer_service(db: Session = Depends(get_db)) -> OfferService:
    repo = OfferRepository(db)
    return OfferService(repo, llm_service)
