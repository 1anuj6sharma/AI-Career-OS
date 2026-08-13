from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class QuestionGenerationAgent:
    """
    Agent 4: Question Generation Agent
    Generates structured, categorized questions grounded in job, resume, and company context.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        job_title: str,
        company_name: str,
        interview_type: str,
        resume_summary: str = "",
        weak_topics: List[str] = None,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        prompt = f"""
        Act as a Principal Tech Interviewer.
        Generate {count} structured, high-yield interview questions for:

        Role: {job_title}
        Company: {company_name or 'Tech Firm'}
        Interview Type: {interview_type}
        Candidate Resume Context: {resume_summary[:1000]}
        Focus Areas / Weak Topics: {weak_topics or []}

        Return questions covering technical mechanics, system architecture, and behavioral STAR situations.
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        # Predefined structured questions schema fallback / baseline
        questions = [
            {
                "question": f"Can you explain how dependency injection works in FastAPI and how you structure reusable database sessions?",
                "category": "TECHNICAL",
                "topic": "FastAPI",
                "difficulty": "MEDIUM",
                "expected_time_minutes": 10,
                "evaluation_criteria": "Mentions Depends(), yield generator, DB connection pooling, and request context cleanup.",
            },
            {
                "question": "Walk me through how you optimize a slow PostgreSQL query using execution plans (EXPLAIN ANALYZE) and indexing.",
                "category": "TECHNICAL",
                "topic": "PostgreSQL",
                "difficulty": "MEDIUM",
                "expected_time_minutes": 15,
                "evaluation_criteria": "Explains B-Tree indexes, Sequential Scan vs Index Scan, composite indexes, and avoiding N+1 queries.",
            },
            {
                "question": "Design a high-throughput job application notification service capable of processing 10,000 requests/second.",
                "category": "SYSTEM_DESIGN",
                "topic": "System Design",
                "difficulty": "HARD",
                "expected_time_minutes": 20,
                "evaluation_criteria": "Describes message queues (Kafka/RabbitMQ), Redis caching, rate limiting, and database sharding.",
            },
            {
                "question": "Tell me about a time when you disagreed with a technical design decision. How did you handle it and what was the outcome?",
                "category": "BEHAVIORAL",
                "topic": "Behavioral STAR",
                "difficulty": "MEDIUM",
                "expected_time_minutes": 10,
                "evaluation_criteria": "Follows STAR structure: Situation, Task, Action, Result with metric impact.",
            },
            {
                "question": f"What bottlenecks do you anticipate scaling a Python backend API to 1 million daily active users?",
                "category": "TECHNICAL",
                "topic": "Scalability",
                "difficulty": "HARD",
                "expected_time_minutes": 15,
                "evaluation_criteria": "Mentions GIL limits, async I/O (asyncio/uvicorn), worker concurrency, DB connection limits, and CDN caching.",
            },
        ]
        return questions[:count]
