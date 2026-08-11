"""
API v1 Router — Composes all module routers.
"""
from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.profile.router import router as profile_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(profile_router)
