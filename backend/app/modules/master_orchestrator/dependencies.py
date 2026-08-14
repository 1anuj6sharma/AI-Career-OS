from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.modules.ai.services.llm_service import get_llm_service, LLMService
from app.modules.master_orchestrator.repository import MasterOrchestratorRepository
from app.modules.master_orchestrator.service import MasterOrchestratorService


def get_master_orchestrator_repository(db: Session = Depends(get_db)) -> MasterOrchestratorRepository:
    return MasterOrchestratorRepository(db)


def get_master_orchestrator_service(
    repo: MasterOrchestratorRepository = Depends(get_master_orchestrator_repository),
    llm_service: LLMService = Depends(get_llm_service),
) -> MasterOrchestratorService:
    return MasterOrchestratorService(repo, llm_service)
