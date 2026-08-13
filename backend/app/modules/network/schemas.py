from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ProfessionalContactCreate(BaseModel):
    name: str = Field("Rahul Sharma", example="Rahul Sharma")
    role: str = Field("Technical Recruiter", example="Technical Recruiter")
    company: str = Field("TechCorp", example="TechCorp")
    email: Optional[str] = "rahul@techcorp.example"
    profile_url: Optional[str] = "https://linkedin.example/in/rahul-sharma"
    source: str = Field("RECRUITER", example="RECRUITER")


class ProfessionalContactOut(BaseModel):
    id: int
    user_id: int
    name: str
    role: str
    company: str
    email: Optional[str] = None
    profile_url: Optional[str] = None
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutreachGenerateQuery(BaseModel):
    contact_id: int = Field(..., example=1)
    purpose: str = Field("RECRUITER_OUTREACH", example="RECRUITER_OUTREACH")  # CONNECTION, RECRUITER_OUTREACH, REFERRAL, FOLLOW_UP
    opportunity_title: Optional[str] = "Senior Python Backend Engineer"


class OutreachMessageOut(BaseModel):
    id: int
    user_id: int
    contact_id: int
    purpose: str
    subject: Optional[str] = None
    message: str
    status: str  # DRAFT, APPROVED, SENT, REJECTED
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationAnalyzeQuery(BaseModel):
    contact_id: int
    message_text: str = Field("Hi Anuj, we reviewed your profile and would love to schedule a screening call next week.", example="Hi Anuj, we reviewed your profile and would love to schedule a screening call next week.")


class ConversationAnalysisOut(BaseModel):
    intent: str
    sentiment: str
    opportunity_level: str
    recommended_action: str
    suggested_reply: str


class FollowUpOut(BaseModel):
    id: int
    contact_id: int
    due_at: datetime
    status: str
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NetworkingAnalyticsOut(BaseModel):
    total_contacts: int
    active_relationships: int
    pending_outreach_drafts: int
    recruiter_response_rate: float
    referral_conversion_rate: float
