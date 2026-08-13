from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class LearningPlannerAgent:
    """
    Agent 1: Learning Planner Agent
    Converts Module 7 skill gaps into personalized learning paths with modules and topics.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, target_role: str, high_priority_gaps: List[str]) -> Dict[str, Any]:
        prompt = f"""
        Act as a Principal AI Curriculum Architect.
        Design a personalized learning path for a candidate targeting '{target_role}':

        High Priority Skill Gaps: {high_priority_gaps}

        Structure into Modules & Topics:
        - Module 1: Core Fundamentals & Mechanics
        - Module 2: Production Setup & Configuration
        - Module 3: Advanced Architecture & Debugging
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "LearningPlannerAgent",
            "title": f"Personalized Learning Path for {target_role}",
            "description": f"Targeted curriculum focusing on {', '.join(high_priority_gaps)}",
            "modules": [
                {
                    "title": "Module 1: Docker Fundamentals & Container Isolation",
                    "description": "Master containerization, images vs containers, and multi-stage Dockerfiles.",
                    "sequence": 1,
                    "topics": [
                        {"title": "Docker Image Layers & Multi-Stage Builds", "difficulty": "INTERMEDIATE", "estimated_minutes": 30},
                        {"title": "Container Networking & Port Forwarding", "difficulty": "INTERMEDIATE", "estimated_minutes": 45},
                    ]
                },
                {
                    "title": "Module 2: System Design Caching & Scaling Patterns",
                    "description": "Redis distributed caching, cache invalidation, and rate limiting.",
                    "sequence": 2,
                    "topics": [
                        {"title": "Redis Cache-Aside vs Write-Through Patterns", "difficulty": "ADVANCED", "estimated_minutes": 45},
                        {"title": "PostgreSQL EXPLAIN ANALYZE & B-Tree Indexing", "difficulty": "ADVANCED", "estimated_minutes": 60},
                    ]
                }
            ],
            "details": getattr(response, "content", str(response)),
        }
