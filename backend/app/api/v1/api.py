"""
API v1 Router — Composes all module routers (Modules 1–15).
"""
from fastapi import APIRouter

from app.controllers.auth.router import router as auth_router
from app.controllers.profile.router import router as profile_router
from app.controllers.jobs.router import router as jobs_router
from app.controllers.ai.router import router as ai_router
from app.controllers.resumes.router import router as resumes_router
from app.controllers.interviews.router import router as interviews_router
from app.controllers.career.router import router as career_router
from app.controllers.learning.router import router as learning_router
from app.controllers.brand.router import router as brand_router
from app.controllers.opportunities.router import router as opportunities_router
from app.controllers.network.router import router as network_router
from app.controllers.offers.router import router as offers_router
from app.controllers.master_orchestrator.router import router as master_orchestrator_router
from app.controllers.integrations.router import router as integrations_router
from app.controllers.dashboard.router import router as dashboard_router
from app.controllers.career_coach.router import router as career_coach_router

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
api_router.include_router(integrations_router)
api_router.include_router(dashboard_router)
api_router.include_router(career_coach_router)
