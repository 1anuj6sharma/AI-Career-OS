from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.resumes.dependencies import get_resume_service
from app.modules.resumes.service import ResumeService
from app.modules.resumes.schemas import (
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
