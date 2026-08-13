from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.resumes.models import Resume, ResumeVersion


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_resume(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_resume_by_id(self, resume_id: int, user_id: int) -> Optional[Resume]:
        return (
            self.db.query(Resume)
            .options(joinedload(Resume.versions))
            .filter(Resume.id == resume_id, Resume.user_id == user_id)
            .first()
        )

    def list_resumes(self, user_id: int) -> List[Resume]:
        return (
            self.db.query(Resume)
            .options(joinedload(Resume.versions))
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .all()
        )

    def delete_resume(self, resume: Resume) -> None:
        self.db.delete(resume)
        self.db.commit()

    def create_version(self, version: ResumeVersion) -> ResumeVersion:
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_version_by_id(self, version_id: int) -> Optional[ResumeVersion]:
        return (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.id == version_id)
            .first()
        )

    def list_versions_for_resume(self, resume_id: int) -> List[ResumeVersion]:
        return (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.version_number.desc())
            .all()
        )

    def activate_version(self, resume_id: int, version_id: int) -> ResumeVersion:
        self.db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == resume_id
        ).update({"is_active": False})

        version = self.get_version_by_id(version_id)
        if version:
            version.is_active = True
            self.db.commit()
            self.db.refresh(version)
        return version
