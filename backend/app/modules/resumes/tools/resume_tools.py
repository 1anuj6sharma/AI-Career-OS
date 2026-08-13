from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.resumes.models import Resume, ResumeVersion


def get_resume_data(db: Session, user_id: int, resume_id: int) -> Dict[str, Any]:
    """Controlled READ tool: Retrieves resume data."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not resume:
        return {}
    active_ver = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume_id, ResumeVersion.is_active == True)
        .first()
    )
    return {
        "id": resume.id,
        "name": resume.name,
        "filename": resume.original_filename,
        "active_version_id": active_ver.id if active_ver else None,
        "content": active_ver.content if active_ver else "",
        "structured_data": active_ver.structured_data if active_ver else {},
    }


def save_new_resume_version(
    db: Session,
    user_id: int,
    resume_id: int,
    version_name: str,
    content: str,
    change_summary: str,
    job_id: Optional[int] = None,
    created_by: str = "AI",
    structured_data: Optional[Dict[str, Any]] = None,
) -> ResumeVersion:
    """Controlled WRITE tool: Saves a new resume version without overwriting prior versions."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not resume:
        raise Exception("Resume not found")

    # Get max version number
    max_ver = (
        db.query(ResumeVersion)
        .filter(ResumeVersion.resume_id == resume_id)
        .count()
    )
    new_ver_num = max_ver + 1

    # Deactivate current active versions
    db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).update({"is_active": False})

    new_ver = ResumeVersion(
        resume_id=resume_id,
        version_number=new_ver_num,
        version_name=version_name,
        created_by=created_by,
        generation_reason=change_summary,
        job_id=job_id,
        change_summary=change_summary,
        content=content,
        structured_data=structured_data,
        is_active=True,
    )
    db.add(new_ver)
    db.commit()
    db.refresh(new_ver)

    return new_ver
