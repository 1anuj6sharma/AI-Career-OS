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


class ProfessionalContact(Base):
    __tablename__ = "professional_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(200), nullable=False)
    role = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    profile_url = Column(String(500), nullable=True)
    source = Column(String(100), nullable=False, default="USER_PROVIDED")  # RECRUITER, ALUMNI, EMPLOYEE, USER_PROVIDED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="professional_contacts")
    relationships = relationship(
        "Relationship", back_populates="contact", cascade="all, delete-orphan"
    )
    outreach_messages = relationship(
        "OutreachMessageRecord", back_populates="contact", cascade="all, delete-orphan"
    )


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id = Column(
        Integer,
        ForeignKey("professional_contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type = Column(String(100), nullable=False, default="RECRUITER")  # RECRUITER, HIRING_MANAGER, PEER, ALUMNI
    relationship_strength = Column(String(50), nullable=False, default="WEAK")  # WEAK, MODERATE, STRONG
    status = Column(String(50), nullable=False, default="NEW", index=True)  # NEW, CONTACTED, CONNECTED, REFERRAL_DISCUSSION, CLOSED
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    next_follow_up_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="relationships")
    contact = relationship("ProfessionalContact", back_populates="relationships")
    interactions = relationship(
        "NetworkInteraction", back_populates="relationship", cascade="all, delete-orphan"
    )


class NetworkInteraction(Base):
    __tablename__ = "network_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    relationship_id = Column(
        Integer,
        ForeignKey("relationships.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interaction_type = Column(String(50), nullable=False, default="MESSAGE")  # MESSAGE, EMAIL, CALL, INTERVIEW
    direction = Column(String(50), nullable=False, default="OUTBOUND")  # INBOUND, OUTBOUND
    content = Column(Text, nullable=False)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())

    relationship = relationship("Relationship", back_populates="interactions")


class OutreachMessageRecord(Base):
    __tablename__ = "outreach_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id = Column(
        Integer,
        ForeignKey("professional_contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purpose = Column(String(100), nullable=False, default="RECRUITER_OUTREACH")  # CONNECTION, RECRUITER_OUTREACH, REFERRAL, FOLLOW_UP
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)  # DRAFT, APPROVED, SENT, REJECTED
    approved_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="outreach_message_records")
    contact = relationship("ProfessionalContact", back_populates="outreach_messages")


class FollowUpRecord(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id = Column(
        Integer,
        ForeignKey("professional_contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    related_opportunity_id = Column(Integer, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, COMPLETED, CANCELLED
    reason = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="follow_up_records")
