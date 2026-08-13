from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.offers.models import (
    CareerOffer,
    OfferCompensation,
    OfferAnalysisRecord,
    OfferComparisonRecord,
    NegotiationStrategyRecord,
    CareerDecisionRecord,
)


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_offer(self, offer: CareerOffer) -> CareerOffer:
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_offer(self, offer_id: int) -> Optional[CareerOffer]:
        return (
            self.db.query(CareerOffer)
            .options(
                joinedload(CareerOffer.compensation),
                joinedload(CareerOffer.analysis),
                joinedload(CareerOffer.negotiation),
            )
            .filter(CareerOffer.id == offer_id)
            .first()
        )

    def list_offers(self, user_id: int) -> List[CareerOffer]:
        return (
            self.db.query(CareerOffer)
            .options(
                joinedload(CareerOffer.compensation),
                joinedload(CareerOffer.analysis),
            )
            .filter(CareerOffer.user_id == user_id)
            .order_by(CareerOffer.created_at.desc())
            .all()
        )

    def save_compensation(self, comp: OfferCompensation) -> OfferCompensation:
        self.db.add(comp)
        self.db.commit()
        self.db.refresh(comp)
        return comp

    def save_analysis(self, analysis: OfferAnalysisRecord) -> OfferAnalysisRecord:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def save_negotiation(self, neg: NegotiationStrategyRecord) -> NegotiationStrategyRecord:
        self.db.add(neg)
        self.db.commit()
        self.db.refresh(neg)
        return neg

    def save_decision(self, dec: CareerDecisionRecord) -> CareerDecisionRecord:
        self.db.add(dec)
        self.db.commit()
        self.db.refresh(dec)
        return dec
