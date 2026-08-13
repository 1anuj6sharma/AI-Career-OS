from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.brand.dependencies import get_brand_service
from app.modules.brand.service import BrandService
from app.modules.brand.schemas import (
    PortfolioProfileOut,
    BrandAnalysisOut,
    LinkedInOptimizeOut,
    ContentGenerateQuery,
    ContentItemOut,
)

router = APIRouter(prefix="/brand", tags=["Module 9 — AI Portfolio & Personal Branding Engine"])


@router.post(
    "/ai/analyze",
    response_model=Dict[str, Any] if False else None,  # Loose return or Schema
    summary="Run closed-loop brand analysis and compute explainable brand score",
)
def analyze_brand(
    target_role: Optional[str] = Query(None, description="Target career role"),
    github_username: Optional[str] = Query(None, description="GitHub username for repository inspection"),
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
    db: Session = Depends(get_db),
):
    return service.analyze_brand(db, current_user.id, target_role, github_username)


@router.post(
    "/ai/generate-portfolio",
    response_model=PortfolioProfileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate role-adapted professional portfolio and technical case studies",
)
def generate_portfolio(
    target_role: Optional[str] = Query(None, description="Target role for portfolio customization"),
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
    db: Session = Depends(get_db),
):
    return service.generate_portfolio(db, current_user.id, target_role)


@router.get(
    "/portfolio",
    response_model=PortfolioProfileOut,
    summary="Get active portfolio profile and technical case studies",
)
def get_active_portfolio(
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
):
    return service.get_active_portfolio(current_user.id)


@router.post(
    "/ai/optimize-profile",
    response_model=LinkedInOptimizeOut,
    summary="Generate LinkedIn headline, about section, and keyword optimization recommendations",
)
def optimize_linkedin(
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
    db: Session = Depends(get_db),
):
    return service.optimize_linkedin(db, current_user.id)


@router.post(
    "/ai/generate-content",
    response_model=ContentItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate technical articles, LinkedIn posts, or READMEs grounded in Personal Brand RAG evidence",
)
def generate_content(
    payload: ContentGenerateQuery,
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
):
    return service.generate_content(current_user.id, payload.content_type, payload.topic)


@router.get(
    "/content",
    response_model=List[ContentItemOut],
    summary="List all generated technical articles and content items",
)
def list_content_items(
    current_user: User = Depends(get_current_active_user),
    service: BrandService = Depends(get_brand_service),
):
    return service.list_content_items(current_user.id)
