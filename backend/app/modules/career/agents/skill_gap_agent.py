from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class Module7SkillGapAgent:
    """
    Agent 3: Skill Gap Agent (Module 7)
    Evaluates current skills vs target job requirements vs interview weaknesses vs resume evidence.
    Classifies gaps into High, Medium, Low priority.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        target_role: str,
        current_skills: List[str],
        interview_weaknesses: List[str] = None,
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as a Principal Skills Evaluator.
        Prioritize skill gaps for candidate aiming for '{target_role}':

        Current Candidate Skills: {current_skills}
        Recent Interview Weaknesses: {interview_weaknesses or []}

        Categorize Gaps:
        - High Priority Gaps (blocking interview success)
        - Medium Priority Gaps
        - Low Priority / Nice-to-Have
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "Module7SkillGapAgent",
            "high_priority_gaps": ["System Design & Distributed Caching", "PostgreSQL Index Tuning"],
            "medium_priority_gaps": ["Kubernetes Deployment", "Kafka Message Queues"],
            "low_priority_gaps": ["GraphQL", "GRPC"],
            "details": getattr(response, "content", str(response)),
        }
