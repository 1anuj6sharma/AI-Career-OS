from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.controllers.network.repository import NetworkRepository
from app.controllers.network.service import NetworkService
from app.controllers.ai.services.llm_service import LLMService

llm_service = LLMService()


def get_network_service(db: Session = Depends(get_db)) -> NetworkService:
    repo = NetworkRepository(db)
    return NetworkService(repo, llm_service)
