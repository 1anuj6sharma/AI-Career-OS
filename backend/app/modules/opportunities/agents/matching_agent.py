from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService
from app.modules.opportunities.tools.opportunity_tools import calculate_hybrid_match_scores


class MatchingAgent:
    """
    Agent 2: AI Job Matching Agent
    Computes multi-dimensional match breakdown (Skill Match, Experience Match, Project Match, Resume Match, Career Match) using hybrid scoring.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        candidate_skills: List[str],
        candidate_exp: float,
        required_skills: List[str],
        preferred_skills: List[str],
        min_exp: float,
    ) -> Dict[str, Any]:
        # 1. Deterministic hybrid scoring
        scores = calculate_hybrid_match_scores(
            candidate_skills, candidate_exp, required_skills, preferred_skills, min_exp
        )

        prompt = f"""
        Act as a Technical Hiring Director.
        Provide match analysis based on hybrid evaluation scores:
        {scores}

        Explain why candidate matches or falls short for the target role.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        scores["analysis_summary"] = getattr(response, "content", str(response))
        scores["agent"] = "MatchingAgent"
        return scores
