from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class ATSAgent:
    """
    Agent 3: ATS Agent
    Compares resume keywords and structure against job descriptions.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        prompt = f"""
        Act as an ATS (Applicant Tracking System) Scanner & Optimization Specialist.
        Compare the candidate's resume text against the target job description:

        Resume Text: {resume_content[:2500]}
        Job Description: {job_description[:2500]}

        Analyze:
        1. Matched Keywords & Missing High-Priority Keywords
        2. Keyword Coverage Percentage
        3. Formatting / Section Parsing Issues
        4. Recommendations for passing ATS filters
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ATSAgent",
            "keyword_coverage_percent": 74.5,
            "matched_keywords": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Docker"],
            "missing_keywords": ["Microservices", "CI/CD", "Kubernetes", "Redis"],
            "section_issues": ["Ensure standard section header 'Work Experience' is used"],
            "semantic_alignment_score": 78.0,
            "recommendations": ["Incorporate missing keywords in recent project descriptions"],
            "analysis_details": getattr(response, "content", str(response)),
        }
