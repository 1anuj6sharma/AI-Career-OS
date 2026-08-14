"""
API v1 Router — Composes all module routers (Modules 1–15).
"""
from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.profile.router import router as profile_router
from app.modules.jobs.router import router as jobs_router
from app.modules.ai.router import router as ai_router
from app.modules.resumes.router import router as resumes_router
from app.modules.interviews.router import router as interviews_router
from app.modules.career.router import router as career_router
from app.modules.learning.router import router as learning_router
from app.modules.brand.router import router as brand_router
from app.modules.opportunities.router import router as opportunities_router
from app.modules.network.router import router as network_router
from app.modules.offers.router import router as offers_router
from app.modules.master_orchestrator.router import router as master_orchestrator_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(jobs_router)
api_router.include_router(ai_router)
api_router.include_router(resumes_router)
api_router.include_router(interviews_router)
api_router.include_router(career_router)
api_router.include_router(learning_router)
api_router.include_router(brand_router)
api_router.include_router(opportunities_router)
api_router.include_router(network_router)
api_router.include_router(offers_router)
api_router.include_router(master_orchestrator_router)
