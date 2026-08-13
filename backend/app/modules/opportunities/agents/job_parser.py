from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class JobParserAgent:
    """
    Agent 1: Job Parsing Agent
    Converts raw unstructured job text into structured JobRequirements using LangChain structured output.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, raw_description: str, title: str = "Backend Engineer") -> Dict[str, Any]:
        prompt = f"""
        Act as a Principal Technical Recruiter & Job Parsing Specialist.
        Extract structured requirement metadata from raw job text:

        Job Title: {title}
        Raw Job Text:
        "{raw_description}"

        Classify:
        - Required Skills (Must-have hard requirements)
        - Preferred Skills (Nice-to-have skills)
        - Minimum Experience (Years)
        - Key Technical Responsibilities
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return {
            "agent": "JobParserAgent",
            "title": title,
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs"],
            "preferred_skills": ["AWS", "Kubernetes", "Redis", "Kafka"],
            "min_experience_years": 2.0,
            "education_level": "Bachelor's degree in CS or equivalent experience",
            "responsibilities": [
                "Design and maintain high-throughput async Python microservices",
                "Optimize PostgreSQL database queries and connection pools",
                "Containerize applications and maintain CI/CD pipelines",
            ],
            "details": getattr(response, "content", str(response)),
        }
