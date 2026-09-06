from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.controllers.auth.dependencies import get_current_active_user
from app.controllers.career_coach.service import CareerCoachService
from app.database.session import get_db
from app.models.auth import User
from app.models.career import CareerRoadmap

router = APIRouter(prefix="/career-coach", tags=["Advanced AI Career Coach"])


class ChatIn(BaseModel):
    message: str = Field(min_length=2, max_length=4000)


class RoadmapIn(BaseModel):
    days: int
    target_role: Optional[str] = Field(default=None, max_length=200)


class StartActionIn(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    rationale: str = ""
    priority: str = "HIGH"
    impact: str = "HIGH"
    effort: str = "MEDIUM"
    urgency: str = "HIGH"
    estimated_minutes: int = Field(default=30, ge=5, le=480)
    confidence: int = Field(default=70, ge=0, le=100)
    evidence: list[str] = []
    task_id: Optional[int] = None


class TaskStatusIn(BaseModel):
    status: str


class InterviewIn(BaseModel):
    mode: str
    job_id: Optional[int] = None


class InterviewAnswerIn(BaseModel):
    question_id: int
    answer: str = Field(min_length=10, max_length=10000)


class DecisionIn(BaseModel):
    question: str = Field(min_length=5, max_length=4000)


class MemoryIn(BaseModel):
    memory_type: str = Field(min_length=2, max_length=50)
    content: str = Field(min_length=2, max_length=2000)
    context_data: Optional[Dict[str, Any]] = None


class FeedbackIn(BaseModel):
    feedback: str


def coach(db: Session, user: User) -> CareerCoachService:
    return CareerCoachService(db, user.id)


def guarded(call):
    try:
        return call()
    except ValueError as exc:
        raise HTTPException(status_code=404 if "not found" in str(exc).lower() else 422, detail=str(exc))


@router.get("/profile")
def profile(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    c = coach(db, current_user).context()
    p = c["profile"]
    return {"career_stage": "Established" if p and (p.years_of_experience or 0) >= 3 else "Early career", "current_role": p.current_role if p else None, "target_role": c["target_role"] or None, "target_industry": None, "skills": [{"name": s.name, "proficiency": s.proficiency_level} for s in c["skills"]], "goals": [{"id": g.id, "title": g.title, "status": g.status} for g in c["goals"]]}


@router.get("/health")
def health(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).health()


@router.get("/brief")
def brief(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).daily_brief()


@router.get("/insights")
def insights(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    service = coach(db, current_user)
    return {"weekly_strategy": service.weekly_strategy(), "application_strategy": service.application_strategy(), "gaps": service.gap_analysis()["gaps"][:3]}


@router.get("/next-action")
def next_action(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).next_action()


@router.post("/next-action/start")
def start_next_action(payload: StartActionIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).start_next_action(payload.model_dump()))


@router.get("/gap-analysis")
def gaps(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).gap_analysis()


@router.post("/roadmap")
def roadmap(payload: RoadmapIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).roadmap(payload.days, payload.target_role))


@router.get("/roadmap")
def active_roadmap(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    roadmap = db.query(CareerRoadmap).filter_by(user_id=current_user.id, status="ACTIVE").order_by(CareerRoadmap.created_at.desc()).first()
    return {"roadmap": None if not roadmap else {"id": roadmap.id, "target_role": roadmap.target_role, "objective": roadmap.objective, "data": roadmap.roadmap_data}}


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskStatusIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).update_task(task_id, payload.status.upper()))


@router.post("/chat")
def chat(payload: ChatIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).chat(payload.message)


@router.post("/job-analysis/{job_id}")
def job_analysis(job_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).job_match(job_id))


@router.post("/resume-analysis")
def resume_analysis(job_id: Optional[int] = None, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).resume_analysis(job_id))


@router.post("/interview")
def interview(payload: InterviewIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).start_interview(payload.mode, payload.job_id))


@router.post("/interview/{interview_id}/answer")
def interview_answer(interview_id: int, payload: InterviewAnswerIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).answer_interview(interview_id, payload.question_id, payload.answer))


@router.post("/decision")
def decision(payload: DecisionIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).decision(payload.question)


@router.post("/memories")
def memory(payload: MemoryIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return coach(db, current_user).store_memory(payload.memory_type, payload.content, payload.context_data)


@router.post("/recommendations/{recommendation_id}/feedback")
def recommendation_feedback(recommendation_id: int, payload: FeedbackIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return guarded(lambda: coach(db, current_user).feedback(recommendation_id, payload.feedback.upper()))
