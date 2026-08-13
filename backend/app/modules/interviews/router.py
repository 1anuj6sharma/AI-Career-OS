from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.interviews.dependencies import get_interview_service
from app.modules.interviews.service import InterviewService
from app.modules.interviews.schemas import (
    InterviewCreate,
    InterviewOut,
    InterviewAnswerCreate,
    PreparationPlanOut,
    InterviewReportOut,
)

router = APIRouter(prefix="/interviews", tags=["Module 6 — Interview Intelligence & AI Coach"])


@router.post(
    "",
    response_model=InterviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule or create a new interview session",
)
def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_resume_service if False else get_interview_service),
):
    return service.create_interview(
        user_id=current_user.id,
        title=payload.title,
        company_name=payload.company_name,
        job_id=payload.job_id,
        resume_version_id=payload.resume_version_id,
        interview_type=payload.interview_type,
        scheduled_at=payload.scheduled_at,
    )


@router.get(
    "",
    response_model=List[InterviewOut],
    summary="List all interview sessions",
)
def list_interviews(
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
):
    return service.list_interviews(current_user.id)


@router.get(
    "/{interview_id}",
    response_model=InterviewOut,
    summary="Get interview details and questions",
)
def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
):
    return service.get_interview(interview_id, current_user.id)


@router.post(
    "/{interview_id}/prepare",
    response_model=PreparationPlanOut,
    summary="Run Interview Strategy, Job Analysis, Company Research & Schedule Module 3 Prep Tasks",
)
def prepare_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
    db: Session = Depends(get_db),
):
    return service.prepare_interview(db, interview_id, current_user.id)


@router.post(
    "/{interview_id}/start",
    response_model=InterviewOut,
    summary="Start live Mock Interview session",
)
def start_mock_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
):
    return service.start_mock_interview(current_user.id, interview_id)


@router.post(
    "/{interview_id}/questions/{question_id}/answer",
    summary="Submit answer for a question and receive real-time evaluation feedback",
)
def submit_answer(
    interview_id: int,
    question_id: int,
    payload: InterviewAnswerCreate,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
):
    return service.submit_question_answer(
        user_id=current_user.id,
        interview_id=interview_id,
        question_id=question_id,
        answer_text=payload.answer,
        duration_seconds=payload.duration_seconds or 60,
    )


@router.get(
    "/{interview_id}/report",
    response_model=InterviewReportOut,
    summary="Generate comprehensive final Interview Report & Performance breakdown",
)
def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    service: InterviewService = Depends(get_interview_service),
):
    return service.generate_interview_report(current_user.id, interview_id)
