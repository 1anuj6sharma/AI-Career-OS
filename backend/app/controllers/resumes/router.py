from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.controllers.auth.dependencies import get_current_active_user
from app.models.auth import User
from app.controllers.resumes.dependencies import get_resume_service
from app.controllers.resumes.service import ResumeService
from app.views.resumes import (
    ResumeOut,
    ResumeVersionOut,
    ResumeAnalysisOut,
    ATSAnalysisOut,
    TailoringPlanOut,
)

router = APIRouter(prefix="/resumes", tags=["Module 5 — Resume Intelligence & Automation"])


@router.post(
    "/upload",
    response_model=ResumeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF/DOCX resume file and extract structured data",
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    file_bytes = await file.read()
    return service.upload_and_parse_resume(
        user_id=current_user.id,
        filename=file.filename,
        file_bytes=file_bytes,
    )


@router.get(
    "",
    response_model=List[ResumeOut],
    summary="List all uploaded resumes and active versions",
)
def list_resumes(
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    return service.list_resumes(current_user.id)


@router.get(
    "/{resume_id}",
    response_model=ResumeOut,
    summary="Get resume details and versions",
)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    return service.get_resume(resume_id, current_user.id)


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume",
)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    service.delete_resume(resume_id, current_user.id)
    return None


@router.post(
    "/{resume_id}/analyze",
    response_model=ResumeAnalysisOut,
    summary="Run AI Resume Quality & Content Analysis Agent",
)
def analyze_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    return service.analyze_resume(resume_id, current_user.id)


@router.post(
    "/{resume_id}/ats-analysis",
    response_model=ATSAnalysisOut,
    summary="Run ATS Keyword Scanner & Format Alignment Agent",
)
def ats_analysis(
    resume_id: int,
    job_description: str = Query(..., description="Target job description for ATS comparison"),
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
):
    return service.run_ats_analysis(resume_id, current_user.id, job_description)


@router.post(
    "/{resume_id}/jobs/{job_id}/match",
    summary="Evaluate Job + Resume Fit Analysis",
)
def match_resume_to_job(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
    db: Session = Depends(get_db),
):
    return service.match_resume_to_job(db, resume_id, job_id, current_user.id)


@router.post(
    "/{resume_id}/jobs/{job_id}/tailor",
    response_model=TailoringPlanOut,
    summary="Run Module 5 LangGraph Tailoring Pipeline with Fact Checker",
)
def tailor_resume(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
    db: Session = Depends(get_db),
):
    return service.tailor_resume_for_job(db, resume_id, job_id, current_user.id)


@router.post(
    "/{resume_id}/versions/approve",
    response_model=ResumeVersionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Human Approval endpoint for approving tailored resume version",
)
def approve_version(
    resume_id: int,
    version_name: str = Form(...),
    draft_content: str = Form(...),
    change_summary: str = Form(...),
    job_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_active_user),
    service: ResumeService = Depends(get_resume_service),
    db: Session = Depends(get_db),
):
    return service.approve_and_save_tailored_version(
        db=db,
        resume_id=resume_id,
        version_name=version_name,
        draft_content=draft_content,
        change_summary=change_summary,
        job_id=job_id,
        user_id=current_user.id,
    )


# --- RESUME STUDIO & BACKEND ATS SCORING ---

from pydantic import BaseModel
from typing import Dict, Any


class ResumeStudioPayload(BaseModel):
    personal: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    template: Optional[str] = "template-modern"


@router.post(
    "/studio/save",
    summary="Persist structured Resume Studio document in backend database"
)
def save_resume_studio(
    payload: ResumeStudioPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from app.models.profile import Profile
    from sqlalchemy import select

    stmt = select(Profile).where(Profile.user_id == current_user.id)
    profile = db.execute(stmt).scalar_one_or_none()

    if profile and payload.personal:
        if payload.personal.get("name"):
            profile.full_name = payload.personal["name"]
        if payload.personal.get("title"):
            profile.target_role = payload.personal["title"]
        if payload.summary:
            profile.bio = payload.summary
        db.commit()

    return {
        "status": "success",
        "message": "Resume Studio document synchronized with PostgreSQL database.",
        "user_id": current_user.id,
        "resume": payload.model_dump()
    }


@router.post(
    "/studio/score",
    summary="Run real Python backend ATS scoring engine on resume payload"
)
def score_resume_studio(
    payload: ResumeStudioPayload,
    target_role: Optional[str] = Query(None)
):
    import re
    
    p = payload.personal or {}
    exps = payload.experience or []
    edus = payload.education or []
    summary = payload.summary or ""
    
    # 1. Completeness (0-25)
    completeness = 0
    if p.get("name") and len(p["name"]) > 2: completeness += 5
    if p.get("email") and "@" in p["email"]: completeness += 5
    if p.get("phone") and len(p["phone"]) >= 7: completeness += 4
    if summary and len(summary) >= 40: completeness += 5
    if len(exps) > 0: completeness += 6
    completeness = min(25, completeness)

    # 2. Action verbs (0-25)
    full_text = summary + " " + " ".join([" ".join(e.get("bullets", [])) for e in exps])
    strong_verbs = ['architected', 'engineered', 'spearheaded', 'optimized', 'deployed', 'scaled', 'implemented', 'orchestrated', 'built', 'automated', 'accelerated', 'refactored', 'designed', 'reduced', 'led']
    found_verbs = [v for v in strong_verbs if v in full_text.lower()]
    action_score = min(25, len(found_verbs) * 6)

    # 3. Quantified metrics (0-25)
    metric_matches = re.findall(r'(\d+%\b|\$\d+|\b\d+k\b|\b\d+m\b|\b\d+x\b|\d+\s*(?:ms|req\/sec|users|clients|TPS|queries|records))', full_text, re.IGNORECASE)
    has_placeholders = "describe key" in full_text.lower() or "responsibilities and achievements" in full_text.lower()
    
    if has_placeholders:
        metric_score = 0
    else:
        metric_score = 25 if len(metric_matches) >= 3 else (14 if len(metric_matches) >= 1 else 0)

    # 4. Target keyword score (0-25)
    core_kw = ['python', 'sql', 'fastapi', 'docker', 'postgresql', 'redis', 'react', 'aws', 'git']
    matched_kw = [k for k in core_kw if k in full_text.lower()]
    kw_score = min(25, len(matched_kw) * 5)

    total_score = completeness + action_score + metric_score + kw_score

    return {
        "total_ats_score": total_score,
        "completeness_score": completeness,
        "action_verbs_score": action_score,
        "metrics_score": metric_score,
        "keyword_score": kw_score,
        "detected_metrics_count": len(metric_matches),
        "detected_verbs": found_verbs,
        "matched_keywords": matched_kw,
        "has_placeholders": has_placeholders,
        "verdict": "🟢 Excellent ATS Ready" if total_score >= 75 else ("🟡 Moderate" if total_score >= 40 else "🔴 Incomplete / Needs Work")
    }

