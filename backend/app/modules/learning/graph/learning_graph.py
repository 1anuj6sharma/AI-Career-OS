from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.learning.agents import (
    LearningPlannerAgent,
    ResourceDiscoveryAgent,
    TutorAgent,
    PracticeAgent,
    AssessmentAgent,
    AdaptiveLearningAgent,
)


class LearningGraphOrchestrator:
    """
    Module 8 LangGraph Stateful Workflow Engine.
    Orchestrates skill gap ingestion, learning path generation, AI tutoring, practice generation, assessment, and adaptive remediation.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.planner = LearningPlannerAgent(llm_service)
        self.resource_agent = ResourceDiscoveryAgent(llm_service)
        self.tutor = TutorAgent(llm_service)
        self.practice_agent = PracticeAgent(llm_service)
        self.assessment_agent = AssessmentAgent(llm_service)
        self.adaptive_agent = AdaptiveLearningAgent(llm_service)

    def generate_learning_path_pipeline(
        self, target_role: str, high_priority_gaps: List[str]
    ) -> Dict[str, Any]:
        path_plan = self.planner.run(target_role, high_priority_gaps)

        # Attach ranked resources to each topic
        for mod in path_plan.get("modules", []):
            for top in mod.get("topics", []):
                top["resources"] = self.resource_agent.run(top["title"])

        return path_plan

    def tutor_query_pipeline(self, topic: str, question: str, mode: str = "INTERMEDIATE") -> Dict[str, Any]:
        return self.tutor.run(topic, question, mode)

    def generate_practice_pipeline(self, topic: str) -> Dict[str, Any]:
        return self.practice_agent.run(topic)

    def assess_submission_pipeline(
        self, db: Session, user_id: int, topic_title: str, submission_text: str
    ) -> Dict[str, Any]:
        eval_result = self.assessment_agent.run(db, user_id, topic_title, submission_text)

        # Check adaptive remediation if failed
        if not eval_result["passed"]:
            adapt_res = self.adaptive_agent.run(topic_title, [eval_result["score"]])
            eval_result["remedial_action"] = adapt_res.get("remedial_topic")

        return eval_result
