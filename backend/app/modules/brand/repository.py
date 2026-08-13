from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.brand.models import (
    PortfolioProfile,
    PortfolioProject,
    CareerBrandProfile,
    BrandScore,
    ContentItem,
    GitHubAnalysis,
    ProfileRecommendation,
)


class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, portfolio: PortfolioProfile) -> PortfolioProfile:
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_active_portfolio(self, user_id: int) -> Optional[PortfolioProfile]:
        return (
            self.db.query(PortfolioProfile)
            .options(joinedload(PortfolioProfile.projects))
            .filter(PortfolioProfile.user_id == user_id)
            .order_by(PortfolioProfile.created_at.desc())
            .first()
        )

    def create_project(self, project: PortfolioProject) -> PortfolioProject:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def save_brand_score(self, score: BrandScore) -> BrandScore:
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def create_content_item(self, item: ContentItem) -> ContentItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_content_items(self, user_id: int) -> List[ContentItem]:
        return (
            self.db.query(ContentItem)
            .filter(ContentItem.user_id == user_id)
            .order_by(ContentItem.created_at.desc())
            .all()
        )

    def get_latest_brand_score(self, user_id: int) -> Optional[BrandScore]:
        return (
            self.db.query(BrandScore)
            .filter(BrandScore.user_id == user_id)
            .order_by(BrandScore.created_at.desc())
            .first()
        )
