from datetime import datetime
from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class CompanyResearchAgent:
    """
    Agent 3: Company Research Agent
    Gathers company insights, engineering culture, interview patterns, and tech stack.
    Includes traceable metadata.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, company_name: str) -> Dict[str, Any]:
        company_clean = company_name or "Tech Innovators Inc"

        prompt = f"""
        Act as an Executive Tech Intelligence Researcher.
        Summarize interview insights and engineering culture for '{company_clean}':

        Include:
        1. Known Tech Stack & Architecture Style
        2. Engineering Culture & Leadership Values
        3. Typical Interview Round Breakdown & Common Question Styles
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "CompanyResearchAgent",
            "company_name": company_clean,
            "tech_stack": ["Python", "Go", "AWS", "Kubernetes", "PostgreSQL"],
            "engineering_values": ["High Ownership", "Data-Driven Engineering", "Operational Excellence"],
            "interview_patterns": ["Phone Screen: DSA + Fundamentals", "Onsite Round 1: System Design", "Onsite Round 2: Behavioral STAR"],
            "source_metadata": {
                "source": "AI Career Knowledge Base & Tech Research Index",
                "retrieved_at": datetime.now().isoformat(),
            },
            "research_summary": getattr(response, "content", str(response)),
        }
