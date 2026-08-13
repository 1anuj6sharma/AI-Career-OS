from typing import Dict, Any
from sqlalchemy.orm import Session
from app.modules.ai.graph.state import CareerGraphState
from app.modules.ai.services.llm_service import LLMService
from app.modules.ai.agents import (
    CareerStrategistAgent,
    JobMatchAgent,
    SkillGapAgent,
    ResumeAgent,
    InterviewAgent,
    PlannerAgent,
)


def classify_intent_node(state: CareerGraphState, llm_service: LLMService) -> CareerGraphState:
    req = state.get("user_request", "").lower()
    intent = "career"

    if "match" in req or "fit" in req or "score" in req:
        intent = "job_match"
        
    elif "gap" in req or "skill" in req or "learn" in req:
        intent = "skill_gap"
    elif "resume" in req or "cv" in req:
        intent = "resume"
    elif "interview" in req or "prep" in req or "question" in req:
        intent = "interview"
    elif "plan" in req or "task" in req or "schedule" in req:
        intent = "planner"

    state["intent"] = intent
    return state


def execute_agent_node(state: CareerGraphState, db: Session, llm_service: LLMService) -> CareerGraphState:
    intent = state.get("intent", "career")
    user_id = state.get("user_id")
    job_id = state.get("job_id")
    results = state.get("agent_results", {})

    if intent == "job_match" and job_id:
        agent = JobMatchAgent(llm_service)
        res = agent.run(db, user_id, job_id)
        results["job_match"] = res
        state["final_response"] = f"Job Match Score: {res.get('overall_score')}%\n\n{res.get('ai_explanation')}"
    elif intent == "skill_gap" and job_id:
        agent = SkillGapAgent(llm_service)
        res = agent.run(db, user_id, job_id)
        results["skill_gap"] = res
        state["final_response"] = res.get("analysis")
    elif intent == "interview" and job_id:
        agent = InterviewAgent(llm_service)
        res = agent.run(db, user_id, job_id)
        results["interview"] = res
        state["final_response"] = res.get("preparation_kit")
    elif intent == "planner":
        agent = PlannerAgent(llm_service)
        res = agent.run(db, user_id)
        results["planner"] = res
        state["final_response"] = res.get("daily_plan")
    elif intent == "resume":
        agent = ResumeAgent(llm_service)
        res = agent.run(db, user_id)
        results["resume"] = res
        state["final_response"] = res.get("suggestions")
    else:
        agent = CareerStrategistAgent(llm_service)
        res = agent.run(db, user_id)
        results["career"] = res
        state["final_response"] = res.get("summary")

    state["agent_results"] = results
    return state
