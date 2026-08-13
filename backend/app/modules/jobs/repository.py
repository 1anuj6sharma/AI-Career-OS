from typing import Optional, List, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

from app.modules.jobs.models import (
    Company,
    Contact,
    Job,
    Application,
    ApplicationEvent,
    JobNote,
    JobTask,
)


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==================== COMPANY ====================

    def create_company(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company_by_id(self, company_id: int, user_id: int) -> Optional[Company]:
        return (
            self.db.query(Company)
            .filter(Company.id == company_id, Company.user_id == user_id)
            .first()
        )

    def list_companies(self, user_id: int) -> List[Company]:
        return (
            self.db.query(Company)
            .filter(Company.user_id == user_id)
            .order_by(Company.name.asc())
            .all()
        )

    def update_company(self, company: Company) -> Company:
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete_company(self, company: Company) -> None:
        self.db.delete(company)
        self.db.commit()

    # ==================== CONTACT ====================

    def create_contact(self, contact: Contact) -> Contact:
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_contact_by_id(self, contact_id: int, user_id: int) -> Optional[Contact]:
        return (
            self.db.query(Contact)
            .options(joinedload(Contact.company))
            .filter(Contact.id == contact_id, Contact.user_id == user_id)
            .first()
        )

    def list_contacts(
        self, user_id: int, company_id: Optional[int] = None
    ) -> List[Contact]:
        query = (
            self.db.query(Contact)
            .options(joinedload(Contact.company))
            .filter(Contact.user_id == user_id)
        )
        if company_id:
            query = query.filter(Contact.company_id == company_id)
        return query.order_by(Contact.name.asc()).all()

    def update_contact(self, contact: Contact) -> Contact:
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, contact: Contact) -> None:
        self.db.delete(contact)
        self.db.commit()

    # ==================== JOB ====================

    def create_job(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_id(self, job_id: int, user_id: int) -> Optional[Job]:
        return (
            self.db.query(Job)
            .options(joinedload(Job.company))
            .filter(Job.id == job_id, Job.user_id == user_id)
            .first()
        )

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
    ) -> Tuple[List[Job], int]:
        query = (
            self.db.query(Job)
            .outerjoin(Company, Job.company_id == Company.id)
            .outerjoin(Application, Job.id == Application.job_id)
            .options(joinedload(Job.company))
            .filter(Job.user_id == user_id)
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_pattern),
                    Job.company_name.ilike(search_pattern),
                    Job.location.ilike(search_pattern),
                    Job.description.ilike(search_pattern),
                    Company.name.ilike(search_pattern),
                )
            )

        if status:
            query = query.filter(Application.status == status)

        if company_id:
            query = query.filter(Job.company_id == company_id)

        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))

        if remote_type:
            query = query.filter(Job.remote_type == remote_type)

        if employment_type:
            query = query.filter(Job.employment_type == employment_type)

        if experience_level:
            query = query.filter(Job.experience_level == experience_level)

        if salary_min is not None:
            query = query.filter(Job.salary_max >= salary_min)

        if salary_max is not None:
            query = query.filter(Job.salary_min <= salary_max)

        if source:
            query = query.filter(Job.source.ilike(f"%{source}%"))

        if is_favorite is not None:
            query = query.filter(Job.is_favorite == is_favorite)

        if is_archived is not None:
            query = query.filter(Job.is_archived == is_archived)

        # Count total matching distinct jobs
        total = query.distinct().count()

        # Paginate
        offset = (page - 1) * page_size
        items = (
            query.distinct()
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_job(self, job: Job) -> Job:
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()

    # ==================== APPLICATION ====================

    def create_application(self, application: Application) -> Application:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application_by_id(
        self, application_id: int, user_id: int
    ) -> Optional[Application]:
        return (
            self.db.query(Application)
            .options(
                joinedload(Application.job).joinedload(Job.company),
                joinedload(Application.recruiter_contact),
                joinedload(Application.events),
                joinedload(Application.tasks),
            )
            .filter(Application.id == application_id, Application.user_id == user_id)
            .first()
        )

    def get_application_by_job_id(
        self, job_id: int, user_id: int
    ) -> Optional[Application]:
        return (
            self.db.query(Application)
            .filter(Application.job_id == job_id, Application.user_id == user_id)
            .first()
        )

    def list_applications(
        self,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Application], int]:
        query = (
            self.db.query(Application)
            .options(
                joinedload(Application.job).joinedload(Job.company),
                joinedload(Application.recruiter_contact),
                joinedload(Application.events),
                joinedload(Application.tasks),
            )
            .filter(Application.user_id == user_id)
        )

        if status:
            query = query.filter(Application.status == status)

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Application.updated_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_application_status_atomic(
        self, application: Application, new_status: str, description: Optional[str] = None
    ) -> Application:
        """
        Updates application status and creates timeline event in a single atomic transaction.
        """
        old_status = application.status
        application.status = new_status
        if new_status == "APPLIED" and not application.applied_at:
            application.applied_at = datetime.now()

        event_desc = (
            description
            if description
            else f"Application status changed from {old_status} to {new_status}"
        )
        event = ApplicationEvent(
            application_id=application.id,
            event_type="STATUS_CHANGE",
            description=event_desc,
            event_date=datetime.now(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(application)
        return application

    def update_application(self, application: Application) -> Application:
        self.db.commit()
        self.db.refresh(application)
        return application

    def delete_application(self, application: Application) -> None:
        self.db.delete(application)
        self.db.commit()

    # ==================== APPLICATION EVENTS (TIMELINE) ====================

    def create_event(self, event: ApplicationEvent) -> ApplicationEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events_for_application(
        self, application_id: int
    ) -> List[ApplicationEvent]:
        return (
            self.db.query(ApplicationEvent)
            .filter(ApplicationEvent.application_id == application_id)
            .order_by(ApplicationEvent.event_date.desc())
            .all()
        )

    # ==================== JOB TASKS ====================

    def create_task(self, task: JobTask) -> JobTask:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[JobTask]:
        return (
            self.db.query(JobTask)
            .filter(JobTask.id == task_id, JobTask.user_id == user_id)
            .first()
        )

    def list_tasks_for_application(
        self, application_id: int, user_id: int
    ) -> List[JobTask]:
        return (
            self.db.query(JobTask)
            .filter(
                JobTask.application_id == application_id, JobTask.user_id == user_id
            )
            .order_by(JobTask.created_at.desc())
            .all()
        )

    def update_task(self, task: JobTask) -> JobTask:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task: JobTask) -> None:
        self.db.delete(task)
        self.db.commit()

    # ==================== JOB NOTES ====================

    def create_note(self, note: JobNote) -> JobNote:
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def list_notes_for_job(self, job_id: int, user_id: int) -> List[JobNote]:
        return (
            self.db.query(JobNote)
            .filter(JobNote.job_id == job_id, JobNote.user_id == user_id)
            .order_by(JobNote.created_at.desc())
            .all()
        )

    def get_note_by_id(self, note_id: int, user_id: int) -> Optional[JobNote]:
        return (
            self.db.query(JobNote)
            .filter(JobNote.id == note_id, JobNote.user_id == user_id)
            .first()
        )

    def delete_note(self, note: JobNote) -> None:
        self.db.delete(note)
        self.db.commit()
