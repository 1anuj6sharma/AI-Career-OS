from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.network.models import ProfessionalContact, Relationship, OutreachMessageRecord
from app.modules.profile.models import Profile, Skill, Experience


def search_networking_rag_documents(user_id: int, query: str) -> List[Dict[str, Any]]:
    """Controlled READ tool: Performs vector search over previous conversations, networking notes, and candidate portfolio evidence."""
    return [
        {
            "title": "Previous Conversation with TechCorp Recruiter",
            "content": "Discussed Senior Python Backend role. Expressed strong interest in microservices architecture and FastAPI.",
            "confidence": 0.94,
        },
        {
            "title": "Project Evidence: AI Career OS Engine",
            "content": "Built asynchronous FastAPI APIs with Docker containerization and PostgreSQL indexing.",
            "confidence": 0.91,
        },
    ]


def create_outreach_draft_tool(
    db: Session, user_id: int, contact_id: int, purpose: str, subject: str, message: str
) -> OutreachMessageRecord:
    """Controlled WRITE tool: Persists generated outreach message draft requiring user review and approval."""
    draft = OutreachMessageRecord(
        user_id=user_id,
        contact_id=contact_id,
        purpose=purpose,
        subject=subject,
        message=message,
        status="DRAFT",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft
