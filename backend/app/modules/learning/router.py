from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.learning.dependencies import get_learning_service
from app.modules.learning.service import LearningService
from app.modules.learning.schemas import (
    LearningPathOut,
    TutorQuery,
    TutorResponse,
    PracticeChallengeOut,
    AssessmentSubmitQuery,
    LearningAssessmentOut,
)

router = APIRouter(prefix="/learning", tags=["Module 8 — AI Learning Hub & Personalized Skill Development"])


@router.post(
    "/ai/generate-path",
    response_model=LearningPathOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized learning path derived from Module 7 skill gaps",
)
def generate_learning_path(
    target_role: Optional[str] = Query(None, description="Target career role"),
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
    db: Session = Depends(get_db),
):
    return service.generate_learning_path(db, current_user.id, target_role)


@router.get(
    "/paths/active",
    response_model=LearningPathOut,
    summary="Get currently active learning path and modules",
)
def get_active_path(
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
):
    return service.get_active_path(current_user.id)


@router.get(
    "/paths",
    response_model=List[LearningPathOut],
    summary="List all historical learning paths",
)
def list_paths(
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
):
    return service.list_paths(current_user.id)


@router.post(
    "/ai/tutor",
    response_model=TutorResponse,
    summary="Ask AI Tutor technical questions with grounded vector RAG documentation retrieval",
)
def ask_ai_tutor(
    payload: TutorQuery,
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
):
    return service.query_tutor(payload.topic, payload.question, payload.mode)


@router.post(
    "/ai/generate-practice",
    response_model=PracticeChallengeOut,
    summary="Generate interactive technical practice problem or Dockerfile challenge",
)
def generate_practice(
    topic: str = Query("Docker", description="Target technical topic for practice"),
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
):
    return service.generate_practice(topic)


@router.post(
    "/ai/assess",
    response_model=LearningAssessmentOut,
    summary="Submit practice solution/quiz response for AI evaluation and update skill proficiency in Module 2",
)
def assess_submission(
    payload: AssessmentSubmitQuery,
    current_user: User = Depends(get_current_active_user),
    service: LearningService = Depends(get_learning_service),
    db: Session = Depends(get_db),
):
    return service.assess_submission(
        db=db,
        user_id=current_user.id,
        topic_id=payload.topic_id,
        topic_title=payload.topic_title,
        submission_text=payload.submission_text,
    )
