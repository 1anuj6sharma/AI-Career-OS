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


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, COMPLETED, ARCHIVED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="learning_paths")
    modules = relationship(
        "LearningModule", back_populates="learning_path", cascade="all, delete-orphan"
    )


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learning_path_id = Column(
        Integer,
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sequence = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learning_path = relationship("LearningPath", back_populates="modules")
    topics = relationship(
        "LearningTopic", back_populates="module", cascade="all, delete-orphan"
    )


class LearningTopic(Base):
    __tablename__ = "learning_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(
        Integer,
        ForeignKey("learning_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    difficulty = Column(String(50), nullable=False, default="INTERMEDIATE")  # BEGINNER, INTERMEDIATE, ADVANCED
    estimated_minutes = Column(Integer, nullable=False, default=30)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("LearningModule", back_populates="topics")
    resources = relationship(
        "LearningResource", back_populates="topic", cascade="all, delete-orphan"
    )


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(
        Integer,
        ForeignKey("learning_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    resource_type = Column(String(50), nullable=False, default="DOCUMENTATION")  # DOCUMENTATION, TUTORIAL, VIDEO, PRACTICE, PROJECT
    url = Column(String(500), nullable=True)
    difficulty = Column(String(50), nullable=False, default="INTERMEDIATE")
    relevance_score = Column(Float, nullable=False, default=90.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("LearningTopic", back_populates="resources")


class LearningAssessment(Base):
    __tablename__ = "learning_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id = Column(
        Integer,
        ForeignKey("learning_topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    score = Column(Float, nullable=False, default=0.0)
    feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="learning_assessments")


class LearningNote(Base):
    __tablename__ = "learning_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id = Column(
        Integer,
        ForeignKey("learning_topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="learning_notes")
