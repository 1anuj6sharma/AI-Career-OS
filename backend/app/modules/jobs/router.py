from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status

from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.jobs.dependencies import get_job_service
from app.modules.jobs.service import JobService
from app.modules.jobs.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyOut,
    ContactCreate,
    ContactUpdate,
    ContactOut,
    JobCreate,
    JobUpdate,
    JobOut,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationOut,
    ApplicationEventCreate,
    ApplicationEventOut,
    JobTaskCreate,
    JobTaskUpdate,
    JobTaskOut,
    JobNoteCreate,
    JobNoteOut,
    PaginatedResponse,
)

router = APIRouter(tags=["Job & Application Management"])


# ==========================================
# JOBS ENDPOINTS
# ==========================================

@router.post(
    "/jobs",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
)
def create_job(
    data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_job(current_user.id, data)


@router.get(
    "/jobs",
    response_model=PaginatedResponse[JobOut],
    summary="List, search, filter, and paginate jobs",
)
def list_jobs(
    search: Optional[str] = Query(None, description="Search term for title, company, location, or description"),
    status: Optional[str] = Query(None, description="Filter by application status"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    location: Optional[str] = Query(None, description="Filter by location"),
    remote_type: Optional[str] = Query(None, description="REMOTE, HYBRID, ONSITE"),
    employment_type: Optional[str] = Query(None, description="FULL_TIME, PART_TIME, etc."),
    experience_level: Optional[str] = Query(None, description="ENTRY_LEVEL, MID_LEVEL, etc."),
    salary_min: Optional[int] = Query(None, description="Minimum salary filter"),
    salary_max: Optional[int] = Query(None, description="Maximum salary filter"),
    source: Optional[str] = Query(None, description="Filter by job source"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites"),
    is_archived: Optional[bool] = Query(None, description="Filter archived"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_jobs(
        user_id=current_user.id,
        search=search,
        status=status,
        company_id=company_id,
        location=location,
        remote_type=remote_type,
        employment_type=employment_type,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        source=source,
        is_favorite=is_favorite,
        is_archived=is_archived,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobOut,
    summary="Get job details",
)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.get_job(job_id, current_user.id)


@router.patch(
    "/jobs/{job_id}",
    response_model=JobOut,
    summary="Update job",
)
def update_job(
    job_id: int,
    data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_job(job_id, current_user.id, data)


@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job",
)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_job(job_id, current_user.id)
    return None


# ==========================================
# APPLICATIONS ENDPOINTS
# ==========================================

@router.post(
    "/jobs/{job_id}/applications",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create application for job",
)
def create_application(
    job_id: int,
    data: ApplicationCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_application(current_user.id, job_id, data)


@router.get(
    "/applications",
    response_model=PaginatedResponse[ApplicationOut],
    summary="List applications with status filter and pagination",
)
def list_applications(
    status: Optional[str] = Query(None, description="Filter by status (SAVED, APPLIED, INTERVIEW, etc.)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_applications(
        user_id=current_user.id, status=status, page=page, page_size=page_size
    )


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationOut,
    summary="Get application details",
)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.get_application(application_id, current_user.id)


@router.patch(
    "/applications/{application_id}",
    response_model=ApplicationOut,
    summary="Update application details",
)
def update_application(
    application_id: int,
    data: ApplicationUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_application(application_id, current_user.id, data)


@router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationOut,
    summary="Update application status with automatic timeline event creation",
)
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_application_status(application_id, current_user.id, data)


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete application",
)
def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_application(application_id, current_user.id)
    return None


# ==========================================
# TIMELINE ENDPOINTS
# ==========================================

@router.get(
    "/applications/{application_id}/timeline",
    response_model=List[ApplicationEventOut],
    summary="Get application history timeline events",
)
def get_timeline(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.get_timeline(application_id, current_user.id)


@router.post(
    "/applications/{application_id}/timeline",
    response_model=ApplicationEventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add manual timeline event to application",
)
def create_timeline_event(
    application_id: int,
    data: ApplicationEventCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_timeline_event(application_id, current_user.id, data)


# ==========================================
# TASKS ENDPOINTS
# ==========================================

@router.get(
    "/applications/{application_id}/tasks",
    response_model=List[JobTaskOut],
    summary="List tasks for application",
)
def list_tasks(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_tasks(application_id, current_user.id)


@router.post(
    "/applications/{application_id}/tasks",
    response_model=JobTaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create task for application",
)
def create_task(
    application_id: int,
    data: JobTaskCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_task(application_id, current_user.id, data)


@router.patch(
    "/tasks/{task_id}",
    response_model=JobTaskOut,
    summary="Update task details or completion status",
)
def update_task(
    task_id: int,
    data: JobTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_task(task_id, current_user.id, data)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_task(task_id, current_user.id)
    return None


# ==========================================
# CONTACTS ENDPOINTS
# ==========================================

@router.get(
    "/contacts",
    response_model=List[ContactOut],
    summary="List user's recruiter and HR contacts",
)
def list_contacts(
    company_id: Optional[int] = Query(None, description="Filter contacts by company ID"),
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_contacts(current_user.id, company_id)


@router.post(
    "/contacts",
    response_model=ContactOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recruiter or HR contact",
)
def create_contact(
    data: ContactCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_contact(current_user.id, data)


@router.patch(
    "/contacts/{contact_id}",
    response_model=ContactOut,
    summary="Update recruiter or HR contact",
)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_contact(contact_id, current_user.id, data)


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
)
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_contact(contact_id, current_user.id)
    return None


# ==========================================
# COMPANIES ENDPOINTS
# ==========================================

@router.get(
    "/companies",
    response_model=List[CompanyOut],
    summary="List companies created by user",
)
def list_companies(
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_companies(current_user.id)


@router.post(
    "/companies",
    response_model=CompanyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create company profile",
)
def create_company(
    data: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_company(current_user.id, data)


@router.patch(
    "/companies/{company_id}",
    response_model=CompanyOut,
    summary="Update company details",
)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.update_company(company_id, current_user.id, data)


@router.delete(
    "/companies/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company profile",
)
def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_company(company_id, current_user.id)
    return None


# ==========================================
# JOB NOTES ENDPOINTS
# ==========================================

@router.get(
    "/jobs/{job_id}/notes",
    response_model=List[JobNoteOut],
    summary="List notes for job",
)
def list_notes(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.list_notes(job_id, current_user.id)


@router.post(
    "/jobs/{job_id}/notes",
    response_model=JobNoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add note to job",
)
def create_note(
    job_id: int,
    data: JobNoteCreate,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    return service.create_note(job_id, current_user.id, data)


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job note",
)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    service: JobService = Depends(get_job_service),
):
    service.delete_note(note_id, current_user.id)
    return None
