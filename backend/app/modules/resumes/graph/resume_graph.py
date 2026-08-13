from typing import Dict, Any
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from app.modules.resumes.graph.state import ResumeGraphState
from app.modules.ai.services.llm_service import LLMService
from app.modules.resumes.agents import (
    ResumeParserAgent,
    ResumeAnalyzerAgent,
    ATSAgent,
    ResumeJobMatchAgent,
    ResumeSkillGapAgent,
    ResumeTailoringAgent,
    FactCheckerAgent,
)


class ResumeGraphOrchestrator:
    """
    Module 5 LangGraph Workflow Engine.
    Orchestrates Parser -> Analyzer -> ATS -> Job Match -> Skill Gap -> Tailoring -> Fact Checker -> Human Review.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run_tailoring_pipeline(
        self, db: Session, user_id: int, resume_id: int, raw_text: str, target_job_id: int, job_title: str, job_description: str
    ) -> Dict[str, Any]:
        # 1. Parse Resume
        parser = ResumeParserAgent(self.llm_service)
        structured = parser.run(raw_text)

        # 2. Analyze Resume
        analyzer = ResumeAnalyzerAgent(self.llm_service)
        analysis = analyzer.run(raw_text, structured.model_dump())

        # 3. ATS Analysis
        ats_agent = ATSAgent(self.llm_service)
        ats_res = ats_agent.run(raw_text, job_description)

        # 4. Job Match
        matcher = ResumeJobMatchAgent(self.llm_service)
        match_res = matcher.run(db, user_id, raw_text, target_job_id)

        # 5. Skill Gap
        skill_gap_agent = ResumeSkillGapAgent(self.llm_service)
        skill_gap_res = skill_gap_agent.run(structured.skills, job_description)

        # 6. Tailoring Agent
        tailor = ResumeTailoringAgent(self.llm_service)
        tailored_draft = tailor.run(raw_text, job_title, job_description)

        # 7. Fact Checker Agent
        checker = FactCheckerAgent(self.llm_service)
        fact_check = checker.run(raw_text, tailored_draft["draft_resume"])

        return {
            "resume_id": resume_id,
            "target_job_id": target_job_id,
            "structured_data": structured.model_dump(),
            "analysis": analysis,
            "ats_analysis": ats_res,
            "job_match": match_res,
            "skill_gap": skill_gap_res,
            "tailoring_plan": tailored_draft["tailoring_plan"],
            "draft_resume": tailored_draft["draft_resume"],
            "fact_check_passed": fact_check["passed"],
            "requires_human_approval": True,
            "approval_status": "PENDING",
        }
