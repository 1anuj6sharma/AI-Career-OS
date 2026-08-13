from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService
from app.modules.offers.tools.offer_tools import calculate_deterministic_compensation_scores


class CompensationAgent:
    """
    Agent 2: Compensation Analyzer Agent
    Combines deterministic compensation arithmetic with LLM explanations of fixed vs variable cash flow.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, base: float, variable: float, joining_bonus: float, bonus: float = 0.0, equity: float = 0.0) -> Dict[str, Any]:
        # 1. Deterministic arithmetic calculation (Mandatory rule: No LLM math)
        comp_scores = calculate_deterministic_compensation_scores(base, variable, joining_bonus, bonus, equity)

        prompt = f"""
        Act as a Compensation Strategy Specialist.
        Explain guaranteed vs potential compensation for candidate based on deterministic calculations:
        {comp_scores}

        Provide clear guidance on fixed income security vs variable risk.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        comp_scores["explanation"] = getattr(response, "content", str(response))
        comp_scores["agent"] = "CompensationAgent"
        return comp_scores
