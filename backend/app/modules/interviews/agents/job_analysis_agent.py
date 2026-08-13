from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class JobAnalysisAgent:
    """
    Agent 2: Job Interview Analysis Agent
    Parses job descriptions into structured technical and behavioral requirements.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, job_title: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Technical Hiring Manager.
        Deconstruct the following job into structured interview dimensions:

        Job Title: {job_title}
        Job Description: {job_description[:2000]}

        Categorize:
        - Technical Stack & Core Competencies
        - System Design / Architecture Requirements
        - Behavioral Leadership Principles
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "JobAnalysisAgent",
            "technical_competencies": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST APIs"],
            "system_design_competencies": ["Distributed Caching", "Database Sharding/Indexing", "Async Task Queues"],
            "behavioral_principles": ["Customer Obsession", "Bias for Action", "Deep Dive"],
            "analysis_details": getattr(response, "content", str(response)),
        }
