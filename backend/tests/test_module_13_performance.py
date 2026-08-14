"""
Unit & Integration Tests for Module 13 — AI Career Performance & Continuous Growth Engine
"""
import pytest
from app.modules.career.services.performance_service import PerformanceService
from app.modules.career.repository import CareerRepository
from app.modules.career.models import CareerGoal, CareerTask, CareerReview
from app.modules.ai.services.llm_service import LLMService
from app.modules.career.agents.performance_agents import (
    CareerPlannerAgent,
    ProductivityAgent,
    PerformanceAnalyzerAgent,
    BlockerDetectionAgent,
    SkillProgressAgent,
    AdaptiveRoadmapAgent,
    CareerRiskAgent,
    CareerScenarioAgent,
    CareerReviewAgent,
    CareerCoachAgent,
)
from app.modules.career.graph.planner_graph import CareerGraphOrchestrator


def test_evidence_skill_confidence_calculation():
    repo = None
    service = PerformanceService(repo)

    # Formula: (0.2 * self) + (0.3 * project) + (0.25 * assessment) + (0.25 * interview)
    # (0.2 * 90) + (0.3 * 80) + (0.25 * 84) + (0.25 * 76) = 18 + 24 + 21 + 19 = 82.0
    score = service.calculate_evidence_skill_confidence(
        self_reported=90.0,
        project_evidence=80.0,
        assessment_score=84.0,
        interview_score=76.0
    )
    assert score == 82.0


def test_specialized_agents_instantiation():
    llm_service = LLMService()

    planner = CareerPlannerAgent(llm_service)
    plan_out = planner.run({"target_role": "Senior Backend Engineer"})
    assert plan_out is not None
    assert len(plan_out.objectives) > 0

    productivity = ProductivityAgent(llm_service)
    daily_out = productivity.run({"pending_tasks": 2})
    assert daily_out is not None
    assert len(daily_out.daily_tasks) > 0

    analyzer = PerformanceAnalyzerAgent(llm_service)
    perf_out = analyzer.run({"performance_score": 85.0})
    assert perf_out.performance_score == 85.0

    blocker = BlockerDetectionAgent(llm_service)
    blocker_out = blocker.run({})
    assert blocker_out.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    coach = CareerCoachAgent(llm_service)
    coach_out = coach.run("How do I prepare for System Design?", {"target_role": "Backend Engineer"})
    assert "reply" in coach_out


def test_langgraph_orchestrator():
    llm_service = LLMService()
    orchestrator = CareerGraphOrchestrator(llm_service)
    assert orchestrator is not None

    coach_resp = orchestrator.get_coach_response("What is my next priority?", {"target_role": "Data Engineer"})
    assert "reply" in coach_resp
