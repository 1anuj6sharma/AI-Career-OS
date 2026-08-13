from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class ResourceDiscoveryAgent:
    """
    Agent 2: Resource Discovery Agent
    Finds and ranks learning resources (Documentation, Tutorials, Videos, Practice, Projects) by relevance score and difficulty.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, topic_title: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Official {topic_title} Production Guide",
                "resource_type": "DOCUMENTATION",
                "url": f"https://docs.example.org/{topic_title.lower().replace(' ', '-')}",
                "difficulty": "INTERMEDIATE",
                "relevance_score": 95.0,
            },
            {
                "title": f"Hands-On {topic_title} Interactive Tutorial",
                "resource_type": "TUTORIAL",
                "url": f"https://tutorials.example.org/{topic_title.lower().replace(' ', '-')}",
                "difficulty": "INTERMEDIATE",
                "relevance_score": 90.0,
            },
            {
                "title": f"{topic_title} Interview Masterclass",
                "resource_type": "PRACTICE",
                "url": f"https://practice.example.org/{topic_title.lower().replace(' ', '-')}",
                "difficulty": "ADVANCED",
                "relevance_score": 88.0,
            },
        ]
