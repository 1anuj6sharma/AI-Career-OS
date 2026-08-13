from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class OpportunitySkillGapAgent:
    """
    Agent 3: Skill Gap Agent (Module 10)
    Extracts missing required/preferred skills and formats them into cross-module action items for Modules 7 & 8.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, missing_skills: List[str], target_role: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Technical Capability Auditor.
        Formulate cross-module learning and project execution goals for missing opportunity skills:

        Target Role: {target_role}
        Missing Skills: {missing_skills}

        Format action items for Module 7 (Execution Plan) and Module 8 (Learning Path).
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "OpportunitySkillGapAgent",
            "missing_skills": missing_skills,
            "module_7_action_items": [f"Create project evidence for {s}" for s in missing_skills],
            "module_8_learning_paths": [f"Master {s} fundamentals" for s in missing_skills],
            "details": getattr(response, "content", str(response)),
        }
