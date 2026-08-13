from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class RankingAgent:
    """
    Agent 5: Opportunity Ranking Agent
    Ranks multiple job opportunities by Match Score, Readiness, Career Alignment, and Skill Gap Cost.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, opportunities_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Sort deterministically by overall match score descending
        sorted_opps = sorted(
            opportunities_list,
            key=lambda x: x.get("latest_match", {}).get("overall_match", 0.0) if isinstance(x.get("latest_match"), dict) else 0.0,
            reverse=True,
        )
        return sorted_opps
