from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime

# --- Profile ---

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    professional_headline: Optional[str] = None
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    preferred_job_type: Optional[str] = None
    preferred_location: Optional[str] = None
    work_preference: Optional[str] = None

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    professional_headline: Optional[str] = None
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    preferred_job_type: Optional[str] = None
    preferred_location: Optional[str] = None
    work_preference: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Skill ---

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    proficiency_level: Optional[str] = None

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    proficiency_level: Optional[str] = None

class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    category: str
    proficiency_level: Optional[str] = None
    created_at: Optional[datetime] = None

# --- Education ---

class EducationCreate(BaseModel):
    degree: str = Field(..., min_length=1, max_length=200)
    institution: str = Field(..., min_length=1, max_length=300)
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[str] = None

class EducationUpdate(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[str] = None

class EducationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Experience ---

class ExperienceCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

class ExperienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    company: str
    role: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Certification ---

class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    issuer: str = Field(..., min_length=1, max_length=300)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_url: Optional[str] = None

class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_url: Optional[str] = None

class CertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Career Preferences ---

class CareerPreferenceUpdate(BaseModel):
    target_roles: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    target_salary_min: Optional[int] = None
    target_salary_max: Optional[int] = None
    preferred_locations: Optional[List[str]] = None
    career_objectives: Optional[str] = None

class CareerPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    target_roles: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    target_salary_min: Optional[int] = None
    target_salary_max: Optional[int] = None
    preferred_locations: Optional[List[str]] = None
    career_objectives: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Full Profile ---

class FullProfileResponse(BaseModel):
    profile: Optional[ProfileResponse] = None
    skills: List[SkillResponse] = []
    education: List[EducationResponse] = []
    experience: List[ExperienceResponse] = []
    certifications: List[CertificationResponse] = []
    career_preferences: Optional[CareerPreferenceResponse] = None

class MessageResponse(BaseModel):
    message: str
