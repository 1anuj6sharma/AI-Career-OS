from datetime import date, datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, model_validator, EmailStr
from app.modules.jobs.constants import (
    ApplicationStatus,
    RemoteType,
    EmploymentType,
    ExperienceLevel,
    TaskPriority,
    TaskStatus,
)

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==========================================
# Company Schemas
# ==========================================

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    size: Optional[str] = Field(None, max_length=50)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    size: Optional[str] = Field(None, max_length=50)


class CompanyOut(CompanyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Contact Schemas
# ==========================================

class ContactBase(BaseModel):
    company_id: Optional[int] = None
    name: str = Field(..., max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    designation: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    company_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    designation: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None


class ContactOut(ContactBase):
    id: int
    user_id: int
    company: Optional[CompanyOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Job Schemas
# ==========================================

class JobBase(BaseModel):
    company_id: Optional[int] = None
    company_name: Optional[str] = Field(None, max_length=200)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    job_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    remote_type: Optional[RemoteType] = RemoteType.REMOTE
    employment_type: Optional[EmploymentType] = EmploymentType.FULL_TIME
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=10)
    source: Optional[str] = Field(None, max_length=100)
    posted_at: Optional[date] = None
    deadline: Optional[date] = None
    is_favorite: bool = False
    is_archived: bool = False

    @model_validator(mode="after")
    def validate_salaries(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company_id: Optional[int] = None
    company_name: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    job_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    remote_type: Optional[RemoteType] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    source: Optional[str] = Field(None, max_length=100)
    posted_at: Optional[date] = None
    deadline: Optional[date] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None

    @model_validator(mode="after")
    def validate_salaries(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobOut(JobBase):
    id: int
    user_id: int
    company: Optional[CompanyOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Application Event Schemas (Timeline)
# ==========================================

class ApplicationEventBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    description: str
    event_date: Optional[datetime] = None


class ApplicationEventCreate(ApplicationEventBase):
    pass


class ApplicationEventOut(ApplicationEventBase):
    id: int
    application_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Job Task Schemas
# ==========================================

class JobTaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING


class JobTaskCreate(JobTaskBase):
    pass


class JobTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    completed_at: Optional[datetime] = None


class JobTaskOut(JobTaskBase):
    id: int
    user_id: int
    application_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Application Schemas
# ==========================================

class ApplicationBase(BaseModel):
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_at: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    recruiter_contact_id: Optional[int] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    description: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    applied_at: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    recruiter_contact_id: Optional[int] = None
    notes: Optional[str] = None


class ApplicationOut(ApplicationBase):
    id: int
    user_id: int
    job_id: int
    job: Optional[JobOut] = None
    recruiter_contact: Optional[ContactOut] = None
    events: List[ApplicationEventOut] = []
    tasks: List[JobTaskOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Job Note Schemas
# ==========================================

class JobNoteBase(BaseModel):
    content: str


class JobNoteCreate(JobNoteBase):
    pass


class JobNoteOut(JobNoteBase):
    id: int
    user_id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
