from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.controllers.brand.repository import BrandRepository
from app.controllers.brand.service import BrandService
from app.controllers.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_brand_service(db: Session = Depends(get_db)) -> BrandService:
    repo = BrandRepository(db)
    return BrandService(repo, llm_service)
