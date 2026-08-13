from typing import Optional, List, Tuple
from datetime import datetime
from math import ceil

from app.core.logging import logger
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.models import (
    Company,
    Contact,
    Job,
    Application,
    ApplicationEvent,
    JobNote,
    JobTask,
)
from app.modules.jobs.schemas import (
    CompanyCreate,
    CompanyUpdate,
    ContactCreate,
    ContactUpdate,
    JobCreate,
    JobUpdate,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationEventCreate,
    JobTaskCreate,
    JobTaskUpdate,
    JobNoteCreate,
)
from app.modules.jobs.exceptions import (
    JobNotFoundException,
    ApplicationNotFoundException,
    CompanyNotFoundException,
    ContactNotFoundException,
    TaskNotFoundException,
    NoteNotFoundException,
    InvalidStatusTransitionException,
)
from app.modules.jobs.constants import ApplicationStatus, TaskStatus


class JobService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    # ==================== COMPANY SERVICES ====================

    def create_company(self, user_id: int, data: CompanyCreate) -> Company:
        company = Company(
            user_id=user_id,
            name=data.name,
            website=data.website,
            size=data.size,
        )
        created = self.repo.create_company(company)
        logger.info(f"Created company '{created.name}' (id={created.id}) for user={user_id}")
        return created

    def get_company(self, company_id: int, user_id: int) -> Company:
        company = self.repo.get_company_by_id(company_id, user_id)
        if not company:
            raise CompanyNotFoundException()
        return company

    def list_companies(self, user_id: int) -> List[Company]:
        return self.repo.list_companies(user_id)

    def update_company(
        self, company_id: int, user_id: int, data: CompanyUpdate
    ) -> Company:
        company = self.get_company(company_id, user_id)
        if data.name is not None:
            company.name = data.name
        if data.website is not None:
            company.website = data.website
        if data.size is not None:
            company.size = data.size
        return self.repo.update_company(company)

    def delete_company(self, company_id: int, user_id: int) -> None:
        company = self.get_company(company_id, user_id)
        self.repo.delete_company(company)
        logger.info(f"Deleted company id={company_id} for user={user_id}")

    # ==================== CONTACT SERVICES ====================

    def create_contact(self, user_id: int, data: ContactCreate) -> Contact:
        if data.company_id:
            self.get_company(data.company_id, user_id)

        contact = Contact(
            user_id=user_id,
            company_id=data.company_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            linkedin_url=data.linkedin_url,
            designation=data.designation,
            notes=data.notes,
        )
        created = self.repo.create_contact(contact)
        logger.info(f"Created contact '{created.name}' (id={created.id}) for user={user_id}")
        return created

    def get_contact(self, contact_id: int, user_id: int) -> Contact:
        contact = self.repo.get_contact_by_id(contact_id, user_id)
        if not contact:
            raise ContactNotFoundException()
        return contact

    def list_contacts(
        self, user_id: int, company_id: Optional[int] = None
    ) -> List[Contact]:
        return self.repo.list_contacts(user_id, company_id)

    def update_contact(
        self, contact_id: int, user_id: int, data: ContactUpdate
    ) -> Contact:
        contact = self.get_contact(contact_id, user_id)

        if data.company_id is not None:
            if data.company_id > 0:
                self.get_company(data.company_id, user_id)
                contact.company_id = data.company_id
            else:
                contact.company_id = None

        if data.name is not None:
            contact.name = data.name
        if data.email is not None:
            contact.email = data.email
        if data.phone is not None:
            contact.phone = data.phone
        if data.linkedin_url is not None:
            contact.linkedin_url = data.linkedin_url
        if data.designation is not None:
            contact.designation = data.designation
        if data.notes is not None:
            contact.notes = data.notes

        return self.repo.update_contact(contact)

    def delete_contact(self, contact_id: int, user_id: int) -> None:
        contact = self.get_contact(contact_id, user_id)
        self.repo.delete_contact(contact)
        logger.info(f"Deleted contact id={contact_id} for user={user_id}")

    # ==================== JOB SERVICES ====================

    def create_job(self, user_id: int, data: JobCreate) -> Job:
        company_name = data.company_name
        if data.company_id:
            company = self.get_company(data.company_id, user_id)
            if not company_name:
                company_name = company.name

        job = Job(
            user_id=user_id,
            company_id=data.company_id,
            company_name=company_name,
            title=data.title,
            description=data.description,
            job_url=data.job_url,
            location=data.location,
            remote_type=data.remote_type.value if data.remote_type else None,
            employment_type=data.employment_type.value if data.employment_type else None,
            experience_level=data.experience_level.value if data.experience_level else None,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            currency=data.currency,
            source=data.source,
            posted_at=data.posted_at,
            deadline=data.deadline,
            is_favorite=data.is_favorite,
            is_archived=data.is_archived,
        )
        created = self.repo.create_job(job)
        logger.info(f"Created job '{created.title}' (id={created.id}) for user={user_id}")
        return created

    def get_job(self, job_id: int, user_id: int) -> Job:
        job = self.repo.get_job_by_id(job_id, user_id)
        if not job:
            raise JobNotFoundException()
        return job

    def list_jobs(
        self,
        user_id: int,
        search: Optional[str] = None,
        status: Optional[str] = None,
        company_id: Optional[int] = None,
        location: Optional[str] = None,
        remote_type: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        source: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        page_size = min(max(page_size, 1), 100)
        page = max(page, 1)

        items, total = self.repo.list_jobs(
            user_id=user_id,
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
        total_pages = ceil(total / page_size) if total > 0 else 1
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def update_job(self, job_id: int, user_id: int, data: JobUpdate) -> Job:
        job = self.get_job(job_id, user_id)

        if data.company_id is not None:
            if data.company_id > 0:
                company = self.get_company(data.company_id, user_id)
                job.company_id = data.company_id
                if not data.company_name:
                    job.company_name = company.name
            else:
                job.company_id = None

        if data.company_name is not None:
            job.company_name = data.company_name
        if data.title is not None:
            job.title = data.title
        if data.description is not None:
            job.description = data.description
        if data.job_url is not None:
            job.job_url = data.job_url
        if data.location is not None:
            job.location = data.location
        if data.remote_type is not None:
            job.remote_type = data.remote_type.value
        if data.employment_type is not None:
            job.employment_type = data.employment_type.value
        if data.experience_level is not None:
            job.experience_level = data.experience_level.value
        if data.salary_min is not None:
            job.salary_min = data.salary_min
        if data.salary_max is not None:
            job.salary_max = data.salary_max
        if data.currency is not None:
            job.currency = data.currency
        if data.source is not None:
            job.source = data.source
        if data.posted_at is not None:
            job.posted_at = data.posted_at
        if data.deadline is not None:
            job.deadline = data.deadline
        if data.is_favorite is not None:
            job.is_favorite = data.is_favorite
        if data.is_archived is not None:
            job.is_archived = data.is_archived

        return self.repo.update_job(job)

    def delete_job(self, job_id: int, user_id: int) -> None:
        job = self.get_job(job_id, user_id)
        self.repo.delete_job(job)
        logger.info(f"Deleted job id={job_id} for user={user_id}")

    # ==================== APPLICATION SERVICES ====================

    def create_application(
        self, user_id: int, job_id: int, data: ApplicationCreate
    ) -> Application:
        job = self.get_job(job_id, user_id)

        # Check if application already exists for this job
        existing = self.repo.get_application_by_job_id(job_id, user_id)
        if existing:
            return existing

        if data.recruiter_contact_id:
            self.get_contact(data.recruiter_contact_id, user_id)

        applied_at = data.applied_at
        if data.status == ApplicationStatus.APPLIED and not applied_at:
            applied_at = datetime.now()

        application = Application(
            user_id=user_id,
            job_id=job_id,
            status=data.status.value,
            applied_at=applied_at,
            application_deadline=data.application_deadline,
            resume_id=data.resume_id,
            cover_letter_id=data.cover_letter_id,
            recruiter_contact_id=data.recruiter_contact_id,
            notes=data.notes,
        )
        created = self.repo.create_application(application)

        # Create initial timeline event
        initial_event = ApplicationEvent(
            application_id=created.id,
            event_type="APPLICATION_CREATED",
            description=f"Application created with status {created.status}",
            event_date=datetime.now(),
        )
        self.repo.create_event(initial_event)

        logger.info(
            f"Created application id={created.id} for job_id={job_id}, user={user_id}"
        )
        return self.get_application(created.id, user_id)

    def get_application(self, application_id: int, user_id: int) -> Application:
        app = self.repo.get_application_by_id(application_id, user_id)
        if not app:
            raise ApplicationNotFoundException()
        return app

    def list_applications(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        page_size = min(max(page_size, 1), 100)
        page = max(page, 1)

        items, total = self.repo.list_applications(
            user_id=user_id, status=status, page=page, page_size=page_size
        )
        total_pages = ceil(total / page_size) if total > 0 else 1
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def update_application_status(
        self, application_id: int, user_id: int, data: ApplicationStatusUpdate
    ) -> Application:
        application = self.get_application(application_id, user_id)
        new_status_str = data.status.value

        if application.status == new_status_str:
            return application

        updated = self.repo.update_application_status_atomic(
            application=application,
            new_status=new_status_str,
            description=data.description,
        )
        logger.info(
            f"Updated application id={application_id} status to {new_status_str} for user={user_id}"
        )
        return self.get_application(updated.id, user_id)

    def update_application(
        self, application_id: int, user_id: int, data: ApplicationUpdate
    ) -> Application:
        application = self.get_application(application_id, user_id)

        if data.recruiter_contact_id is not None:
            if data.recruiter_contact_id > 0:
                self.get_contact(data.recruiter_contact_id, user_id)
                application.recruiter_contact_id = data.recruiter_contact_id
            else:
                application.recruiter_contact_id = None

        if data.status is not None and data.status.value != application.status:
            self.update_application_status(
                application_id, user_id, ApplicationStatusUpdate(status=data.status)
            )
            application = self.get_application(application_id, user_id)

        if data.applied_at is not None:
            application.applied_at = data.applied_at
        if data.application_deadline is not None:
            application.application_deadline = data.application_deadline
        if data.resume_id is not None:
            application.resume_id = data.resume_id
        if data.cover_letter_id is not None:
            application.cover_letter_id = data.cover_letter_id
        if data.notes is not None:
            application.notes = data.notes

        updated = self.repo.update_application(application)
        return self.get_application(updated.id, user_id)

    def delete_application(self, application_id: int, user_id: int) -> None:
        application = self.get_application(application_id, user_id)
        self.repo.delete_application(application)
        logger.info(f"Deleted application id={application_id} for user={user_id}")

    # ==================== TIMELINE SERVICES ====================

    def get_timeline(
        self, application_id: int, user_id: int
    ) -> List[ApplicationEvent]:
        self.get_application(application_id, user_id)
        return self.repo.list_events_for_application(application_id)

    def create_timeline_event(
        self, application_id: int, user_id: int, data: ApplicationEventCreate
    ) -> ApplicationEvent:
        self.get_application(application_id, user_id)
        event = ApplicationEvent(
            application_id=application_id,
            event_type=data.event_type,
            description=data.description,
            event_date=data.event_date or datetime.now(),
        )
        return self.repo.create_event(event)

    # ==================== TASK SERVICES ====================

    def create_task(
        self, application_id: int, user_id: int, data: JobTaskCreate
    ) -> JobTask:
        self.get_application(application_id, user_id)
        task = JobTask(
            user_id=user_id,
            application_id=application_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            priority=data.priority.value,
            status=data.status.value,
        )
        created = self.repo.create_task(task)
        logger.info(f"Created task id={created.id} for application_id={application_id}")
        return created

    def list_tasks(self, application_id: int, user_id: int) -> List[JobTask]:
        self.get_application(application_id, user_id)
        return self.repo.list_tasks_for_application(application_id, user_id)

    def update_task(
        self, task_id: int, user_id: int, data: JobTaskUpdate
    ) -> JobTask:
        task = self.repo.get_task_by_id(task_id, user_id)
        if not task:
            raise TaskNotFoundException()

        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.priority is not None:
            task.priority = data.priority.value
        if data.status is not None:
            task.status = data.status.value
            if data.status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = datetime.now()

        if data.completed_at is not None:
            task.completed_at = data.completed_at

        return self.repo.update_task(task)

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.repo.get_task_by_id(task_id, user_id)
        if not task:
            raise TaskNotFoundException()
        self.repo.delete_task(task)
        logger.info(f"Deleted task id={task_id} for user={user_id}")

    # ==================== JOB NOTES SERVICES ====================

    def create_note(
        self, job_id: int, user_id: int, data: JobNoteCreate
    ) -> JobNote:
        self.get_job(job_id, user_id)
        note = JobNote(
            user_id=user_id,
            job_id=job_id,
            content=data.content,
        )
        return self.repo.create_note(note)

    def list_notes(self, job_id: int, user_id: int) -> List[JobNote]:
        self.get_job(job_id, user_id)
        return self.repo.list_notes_for_job(job_id, user_id)

    def delete_note(self, note_id: int, user_id: int) -> None:
        note = self.repo.get_note_by_id(note_id, user_id)
        if not note:
            raise NoteNotFoundException()
        self.repo.delete_note(note)
