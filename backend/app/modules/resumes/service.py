from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.resumes.repository import ResumeRepository
from app.modules.resumes.models import Resume, ResumeVersion
from app.modules.resumes.exceptions import ResumeNotFoundException, ResumeVersionNotFoundException
from app.modules.resumes.services.document_processor import DocumentProcessor
from app.modules.ai.services.llm_service import LLMService
from app.modules.resumes.agents import (
    ResumeParserAgent,
    ResumeAnalyzerAgent,
    ATSAgent,
    ResumeJobMatchAgent,
    ResumeSkillGapAgent,
)
from app.modules.resumes.graph.resume_graph import ResumeGraphOrchestrator
from app.modules.jobs.models import Job, Application


class ResumeService:
    def __init__(self, repo: ResumeRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = ResumeGraphOrchestrator(llm_service)

    def upload_and_parse_resume(
        self, user_id: int, filename: str, file_bytes: bytes
    ) -> Resume:
        # 1. Extract Text
        raw_text = DocumentProcessor.extract_text(file_bytes, filename)

        # 2. Create Resume Entity
        file_type = filename.split(".")[-1].lower()
        resume = Resume(
            user_id=user_id,
            name=filename.rsplit(".", 1)[0],
            original_filename=filename,
            file_type=file_type,
            status="PARSED",
        )
        created = self.repo.create_resume(resume)

        # 3. Parse Structured Data via ResumeParserAgent
        parser = ResumeParserAgent(self.llm_service)
        structured = parser.run(raw_text)

        # 4. Save Version 1 (Original)
        ver1 = ResumeVersion(
            resume_id=created.id,
            version_number=1,
            version_name="v1.0 Original",
            created_by="USER",
            generation_reason="Original uploaded document",
            content=raw_text,
            structured_data=structured.model_dump(),
            is_active=True,
        )
        self.repo.create_version(ver1)
        logger.info(f"Uploaded and parsed resume id={created.id} for user={user_id}")
        return self.get_resume(created.id, user_id)

    def get_resume(self, resume_id: int, user_id: int) -> Resume:
        resume = self.repo.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundException()
        return resume

    def list_resumes(self, user_id: int) -> List[Resume]:
        return self.repo.list_resumes(user_id)

    def delete_resume(self, resume_id: int, user_id: int) -> None:
        resume = self.get_resume(resume_id, user_id)
        self.repo.delete_resume(resume)

    def analyze_resume(self, resume_id: int, user_id: int) -> Dict[str, Any]:
        resume = self.get_resume(resume_id, user_id)
        active_ver = next((v for v in resume.versions if v.is_active), resume.versions[0])

        analyzer = ResumeAnalyzerAgent(self.llm_service)
        return analyzer.run(active_ver.content, active_ver.structured_data)

    def run_ats_analysis(
        self, resume_id: int, user_id: int, job_description: str
    ) -> Dict[str, Any]:
        resume = self.get_resume(resume_id, user_id)
        active_ver = next((v for v in resume.versions if v.is_active), resume.versions[0])

        ats = ATSAgent(self.llm_service)
        return ats.run(active_ver.content, job_description)

    def match_resume_to_job(
        self, db: Session, resume_id: int, job_id: int, user_id: int
    ) -> Dict[str, Any]:
        resume = self.get_resume(resume_id, user_id)
        active_ver = next((v for v in resume.versions if v.is_active), resume.versions[0])

        matcher = ResumeJobMatchAgent(self.llm_service)
        return matcher.run(db, user_id, active_ver.content, job_id)

    def tailor_resume_for_job(
        self, db: Session, resume_id: int, job_id: int, user_id: int
    ) -> Dict[str, Any]:
        resume = self.get_resume(resume_id, user_id)
        active_ver = next((v for v in resume.versions if v.is_active), resume.versions[0])

        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            raise Exception("Target job not found")

        # Run LangGraph Tailoring Pipeline
        return self.graph_orchestrator.run_tailoring_pipeline(
            db=db,
            user_id=user_id,
            resume_id=resume_id,
            raw_text=active_ver.content,
            target_job_id=job_id,
            job_title=job.title,
            job_description=job.description or "",
        )

    def approve_and_save_tailored_version(
        self, db: Session, resume_id: int, version_name: str, draft_content: str, change_summary: str, job_id: Optional[int], user_id: int
    ) -> ResumeVersion:
        resume = self.get_resume(resume_id, user_id)
        max_num = len(resume.versions) + 1

        # Deactivate old versions
        db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).update({"is_active": False})

        new_ver = ResumeVersion(
            resume_id=resume_id,
            version_number=max_num,
            version_name=version_name,
            created_by="AI",
            generation_reason=change_summary,
            job_id=job_id,
            change_summary=change_summary,
            content=draft_content,
            is_active=True,
        )
        self.repo.create_version(new_ver)

        # Link to Module 3 Application if application exists for job
        if job_id:
            app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user_id).first()
            if app:
                app.resume_version_id = new_ver.id
                db.commit()

        logger.info(f"Approved new resume version {new_ver.version_name} (id={new_ver.id}) for user={user_id}")
        return new_ver
