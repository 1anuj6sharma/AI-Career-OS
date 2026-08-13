from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.services.llm_service import LLMService
from app.modules.interviews.agents import (
    InterviewStrategyAgent,
    JobAnalysisAgent,
    CompanyResearchAgent,
    QuestionGenerationAgent,
    MockInterviewAgent,
    AnswerEvaluationAgent,
    WeaknessDetectionAgent,
    InterviewPlannerAgent,
)


class InterviewGraphOrchestrator:
    """
    Module 6 LangGraph Stateful Workflow Engine.
    Orchestrates Preparation & Adaptive Live Mock Interview Sessions.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def prepare_interview(
        self,
        db: Session,
        user_id: int,
        interview_id: int,
        job_title: str,
        company_name: str,
        interview_type: str,
        job_description: str = "",
        resume_summary: str = "",
        job_id: int = None,
    ) -> Dict[str, Any]:
        # 1. Strategy Agent
        strat_agent = InterviewStrategyAgent(self.llm_service)
        strategy = strat_agent.run(job_title, company_name, interview_type, job_description, resume_summary)

        # 2. Company Research Agent
        company_agent = CompanyResearchAgent(self.llm_service)
        company_insights = company_agent.run(company_name)

        # 3. Question Generation Agent
        q_agent = QuestionGenerationAgent(self.llm_service)
        generated_questions = q_agent.run(job_title, company_name, interview_type, resume_summary, strategy["priority_topics"], count=5)

        # 4. Planner Agent
        planner = InterviewPlannerAgent(self.llm_service)
        prep_plan = planner.run(
            db=db,
            user_id=user_id,
            interview_id=interview_id,
            interview_title=f"{job_title} at {company_name or 'Tech Co'}",
            job_id=job_id,
            priority_topics=strategy["priority_topics"],
        )

        return {
            "interview_id": interview_id,
            "interview_type": interview_type,
            "priority_topics": strategy["priority_topics"],
            "behavioral_topics": strategy["behavioral_topics"],
            "company_insights": company_insights,
            "generated_questions": generated_questions,
            "preparation_tasks_created": prep_plan["tasks_created_count"],
            "strategy_summary": strategy["strategy_summary"],
        }

    def evaluate_user_answer(
        self,
        question_text: str,
        question_category: str,
        evaluation_criteria: str,
        user_answer: str,
    ) -> Dict[str, Any]:
        evaluator = AnswerEvaluationAgent(self.llm_service)
        return evaluator.run(question_text, question_category, evaluation_criteria, user_answer)
