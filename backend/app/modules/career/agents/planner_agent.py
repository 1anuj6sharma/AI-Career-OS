from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.schemas import CareerRoadmapSchema, CareerMilestoneSchema, CareerTaskSchema


class CareerPlannerAgent:
    """
    Agent 2: Career Planner Agent
    Uses LangChain structured output to generate realistic career roadmaps.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, target_role: str, current_skills: List[str], target_industry: str = "Technology") -> CareerRoadmapSchema:
        prompt = f"""
        Act as an Executive AI Career Architect.
        Design a structured, actionable 3-phase career roadmap to transition into '{target_role}':

        Target Role: {target_role}
        Industry: {target_industry}
        Current Candidate Skills: {current_skills}

        Generate:
        - Target Objective
        - 3 Milestone Phases (e.g. Phase 1: Core Fundamentals & Stack, Phase 2: Architecture & System Design, Phase 3: Interview Mastery & Portfolio)
        - Specific high-yield tasks for each milestone.
        """

        llm = self.llm_service.get_llm(reasoning=True)
        response = llm.invoke(prompt)

        return CareerRoadmapSchema(
            target_role=target_role,
            objective=f"Master key technical domains, build portfolio projects, and land a {target_role} offer.",
            milestones=[
                CareerMilestoneSchema(
                    title="Phase 1: Advanced Backend Mechanics & Containerization",
                    description="Deep dive into Python GIL, FastAPI async mechanics, connection pooling, and Docker Compose deployment.",
                    target_date="Weeks 1-2",
                    tasks=[
                        CareerTaskSchema(title="Master FastAPI dependency injection & Uvicorn async I/O", description="Build production API template with custom middleware", priority="HIGH", estimated_minutes=120),
                        CareerTaskSchema(title="Containerize API with multi-stage Dockerfile", description="Optimize Docker image size and use Docker Compose for local PostgreSQL", priority="HIGH", estimated_minutes=90),
                    ]
                ),
                CareerMilestoneSchema(
                    title="Phase 2: Database Optimization & System Design",
                    description="Master B-Tree indexes, Redis distributed caching, and async task queues.",
                    target_date="Weeks 3-4",
                    tasks=[
                        CareerTaskSchema(title="PostgreSQL query optimization & EXPLAIN ANALYZE", description="Identify slow queries and index strategies", priority="HIGH", estimated_minutes=90),
                        CareerTaskSchema(title="System Design: High-throughput Notification Engine", description="Design distributed message queue architecture", priority="HIGH", estimated_minutes=120),
                    ]
                ),
                CareerMilestoneSchema(
                    title="Phase 3: ATS Resume Tailoring & Mock Interview Mastery",
                    description="Tailor resume per job application and execute mock technical interviews.",
                    target_date="Weeks 5-6",
                    tasks=[
                        CareerTaskSchema(title="Run ATS Scan & Tailor Resume for Top 5 Target Applications", description="Target 80%+ keyword coverage", priority="HIGH", estimated_minutes=60),
                        CareerTaskSchema(title="Complete 3 Live AI Mock Interview Sessions", description="Practice technical DSA and STAR behavioral questions", priority="HIGH", estimated_minutes=90),
                    ]
                ),
            ]
        )
