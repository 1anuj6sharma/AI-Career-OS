from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class CareerOffer(Base):
    __tablename__ = "career_offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name = Column(String(200), nullable=False)
    role = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="RECEIVED", index=True)  # RECEIVED, NEGOTIATING, ACCEPTED, REJECTED, EXPIRED
    offer_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    joining_date = Column(DateTime(timezone=True), nullable=True)
    document_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="career_offers")
    compensation = relationship(
        "OfferCompensation", back_populates="offer", uselist=False, cascade="all, delete-orphan"
    )
    analysis = relationship(
        "OfferAnalysisRecord", back_populates="offer", uselist=False, cascade="all, delete-orphan"
    )
    negotiation = relationship(
        "NegotiationStrategyRecord", back_populates="offer", uselist=False, cascade="all, delete-orphan"
    )


class OfferCompensation(Base):
    __tablename__ = "offer_compensation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(
        Integer,
        ForeignKey("career_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    base_salary = Column(Float, nullable=False, default=0.0)
    variable_salary = Column(Float, nullable=False, default=0.0)
    bonus = Column(Float, nullable=False, default=0.0)
    joining_bonus = Column(Float, nullable=False, default=0.0)
    equity = Column(Float, nullable=False, default=0.0)
    benefits = Column(Text, nullable=True)
    total_ctc = Column(Float, nullable=False, default=0.0)
    guaranteed_compensation = Column(Float, nullable=False, default=0.0)

    offer = relationship("CareerOffer", back_populates="compensation")


class OfferAnalysisRecord(Base):
    __tablename__ = "offer_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(
        Integer,
        ForeignKey("career_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    compensation_score = Column(Float, nullable=False, default=80.0)
    career_fit_score = Column(Float, nullable=False, default=85.0)
    growth_score = Column(Float, nullable=False, default=85.0)
    company_score = Column(Float, nullable=False, default=80.0)
    location_score = Column(Float, nullable=False, default=80.0)
    risk_score = Column(Float, nullable=False, default=15.0)  # Lower is safer
    overall_score = Column(Float, nullable=False, default=82.5)
    analysis = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    offer = relationship("CareerOffer", back_populates="analysis")


class OfferComparisonRecord(Base):
    __tablename__ = "offer_comparisons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    offer_a_id = Column(Integer, nullable=False)
    offer_b_id = Column(Integer, nullable=False)
    comparison_data = Column(JSON, nullable=False)
    recommended_offer_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="offer_comparisons")


class NegotiationStrategyRecord(Base):
    __tablename__ = "negotiation_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(
        Integer,
        ForeignKey("career_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_compensation = Column(Float, nullable=False, default=0.0)
    minimum_compensation = Column(Float, nullable=False, default=0.0)
    leverage_score = Column(Float, nullable=False, default=75.0)
    priorities = Column(JSON, nullable=True)
    strategy = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    offer = relationship("CareerOffer", back_populates="negotiation")


class CareerDecisionRecord(Base):
    __tablename__ = "career_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    offer_id = Column(
        Integer,
        ForeignKey("career_offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    decision = Column(String(50), nullable=False, default="NEGOTIATE")  # ACCEPT, NEGOTIATE, WAIT, REJECT
    reasoning = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=85.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="career_decisions")
