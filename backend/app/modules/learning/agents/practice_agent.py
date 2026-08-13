from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class PracticeAgent:
    """
    Agent 4: Practice Agent
    Generates targeted practice problems, Dockerfile tasks, code challenges, and system design exercises.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, topic: str) -> Dict[str, Any]:
        prompt = f"""
        Act as a Technical Exercise Designer.
        Create an interactive practice challenge for '{topic}':

        Include:
        - Challenge Title
        - Problem Statement
        - Starter Configuration / Code Snippet
        - Verification Hints
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "PracticeAgent",
            "topic": topic,
            "challenge_title": f"Production {topic} Multi-Stage Setup Challenge",
            "problem_statement": f"Configure a production-ready setup for {topic} that minimizes container image size and ensures isolation.",
            "starter_code_or_config": f"# Starter Configuration for {topic}\nFROM python:3.11-slim\nWORKDIR /app\nCOPY . .",
            "verification_hints": ["Use multi-stage builds", "Do not expose root credentials", "Inspect container bridge network"],
            "details": getattr(response, "content", str(response)),
        }
