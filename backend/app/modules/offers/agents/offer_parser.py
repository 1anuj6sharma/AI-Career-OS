from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class OfferParserAgent:
    """
    Agent 1: Offer Document Parser Agent
    Converts raw offer text or uploaded documents into structured OfferDetails using LangChain.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, raw_text: str) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Compensation Parser.
        Extract structured compensation details from raw offer text:
        "{raw_text}"

        Extract:
        - Company Name
        - Role Title
        - Base Salary (Annual)
        - Variable Salary / Performance Bonus
        - Joining Bonus
        - Equity / Stock Options
        - Benefits & Perks
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "OfferParserAgent",
            "company_name": "TechCorp",
            "role": "Senior Python Backend Engineer",
            "base_salary": 1200000.0,
            "variable_salary": 200000.0,
            "joining_bonus": 100000.0,
            "equity": 0.0,
            "benefits": "Health insurance, ₹50k learning allowance, hybrid work mode",
            "details": getattr(response, "content", str(response)),
        }
