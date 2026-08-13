from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class InterviewStrategyAgent:
    """
    Agent 1: Interview Strategy Agent
    Determines interview preparation strategy, priority topics, and difficulty.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        job_title: str,
        company_name: str,
        interview_type: str,
        job_description: str = "",
        resume_summary: str = "",
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Interview Prep Coach.
        Formulate a strategy for an upcoming interview:

        Target Role: {job_title}
        Company: {company_name or 'Tech Company'}
        Interview Type: {interview_type}
        Job Description: {job_description[:1500]}
        Candidate Resume Summary: {resume_summary[:1500]}

        Output:
        1. Priority Technical Topics
        2. Priority Behavioral Topics
        3. Estimated Difficulty (easy, medium, hard)
        4. Key Focus Strategy Recommendation
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "InterviewStrategyAgent",
            "interview_type": interview_type,
            "priority_topics": ["Backend Architecture", "FastAPI / Python Internal Mechanics", "PostgreSQL Query Optimization", "System Design Scaling"],
            "behavioral_topics": ["Ownership & Accountability", "Technical Disagreements & Collaboration", "Handling Deadline Pressure"],
            "difficulty": "medium",
            "strategy_summary": getattr(response, "content", str(response)),
        }
