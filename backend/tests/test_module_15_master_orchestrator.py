"""
Unit & Integration Tests for Module 15 — AI Career OS Master Orchestrator & Autonomous Career Agent
"""
import pytest
from app.modules.master_orchestrator.services.module_registry import (
    MODULE_REGISTRY,
    resolve_modules_for_capabilities,
)
from app.modules.master_orchestrator.services.orchestration_service import MasterOrchestrationService
from app.modules.ai.services.llm_service import LLMService
from app.modules.master_orchestrator.agents.master_agents import (
    MasterCareerAgent,
    IntentClassifierAgent,
    PlanningAgent,
    GoalDecompositionAgent,
    ModuleRoutingAgent,
    ReflectionEvaluationAgent,
    AdaptiveStrategyEngineAgent,
)
from app.modules.master_orchestrator.graph.master_graph import MasterGraphOrchestrator


def test_capability_module_registry():
    assert "career_performance" in MODULE_REGISTRY
    assert "opportunity_acquisition" in MODULE_REGISTRY

    resolved = resolve_modules_for_capabilities(["mock_interview", "job_discovery"])
    assert len(resolved) == 2
    codes = [r["module_code"] for r in resolved]
    assert "module_6" in codes
    assert "module_14" in codes


def test_deterministic_next_best_action():
    service = MasterOrchestrationService(repo=None)

    action = service.calculate_next_best_action(db=None, user_id=1)
    assert action is not None
    assert "action_title" in action
    assert action["rank_score"] > 0
    assert action["expected_impact"] in ["HIGH", "MEDIUM", "LOW"]


def test_master_agents_suite():
    llm_service = LLMService()

    classifier = IntentClassifierAgent(llm_service)
    intent_out = classifier.run("Prepare me for my upcoming system design interview")
    assert intent_out.intent == "interview_prep"

    planner = PlanningAgent(llm_service)
    plan_out = planner.run("Senior AI Backend Engineer", {"skills": ["Python"]})
    assert plan_out.goal_title == "Senior AI Backend Engineer"
    assert len(plan_out.phases) == 3

    router_agent = ModuleRoutingAgent(llm_service)
    route_out = router_agent.run(["mock_interview", "opportunity_acquisition"])
    assert len(route_out.selected_modules) > 0

    reflector = ReflectionEvaluationAgent(llm_service)
    refl_out = reflector.run({"applications": 15})
    assert refl_out.recommended_pivot is True


def test_master_langgraph_orchestrator():
    llm_service = LLMService()
    orchestrator = MasterGraphOrchestrator(llm_service)

    route_auto = orchestrator._route_approval_level({"approval_level": "LEVEL_1"})
    assert route_auto == "auto_execute"

    route_await = orchestrator._route_approval_level({"approval_level": "LEVEL_3", "approval_status": "PENDING"})
    assert route_await == "await_approval"
