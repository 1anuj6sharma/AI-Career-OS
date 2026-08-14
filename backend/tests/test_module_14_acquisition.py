"""
Unit & Integration Tests for Module 14 — AI Career Opportunity Intelligence & Job Acquisition Engine
"""
import pytest
from app.modules.opportunities.services.acquisition_service import OpportunityAcquisitionService
from app.modules.opportunities.models import JobOpportunity
from app.modules.ai.services.llm_service import LLMService
from app.modules.opportunities.agents.acquisition_agents import (
    OpportunitySupervisorAgent,
    DiscoveryAgent,
    MatchingAgent,
    ResearchAgent,
    EvaluationAgent,
    StrategyAgent,
    ResumePersonalizationAgent,
    ApplicationAgent,
    TrackingAgent,
    FeedbackLearningAgent,
)
from app.modules.opportunities.graph.opportunity_graph import OpportunityGraphOrchestrator


def test_deterministic_opportunity_scoring():
    service = OpportunityAcquisitionService(repo=None)

    opp = JobOpportunity(
        id=1,
        company_name="Stripe",
        title="Senior Backend Engineer",
        description="We are looking for a Senior Backend Engineer proficient in Python, FastAPI, PostgreSQL, and Docker.",
        salary_min=160000,
        salary_max=200000,
        source="LINKEDIN"
    )

    user_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
    score_rec = service.calculate_opportunity_score(user_skills, "Senior Backend Engineer", opp)

    assert score_rec.overall_score >= 85.0
    assert score_rec.skill_score >= 80.0
    assert score_rec.career_alignment_score == 95.0


def test_specialized_acquisition_agents():
    llm_service = LLMService()

    supervisor = OpportunitySupervisorAgent(llm_service)
    step = supervisor.route_next_step({"opportunity_score": 91.5, "approval_status": "PENDING"})
    assert step == "request_human_approval"

    discovery = DiscoveryAgent(llm_service)
    disc_out = discovery.run({"keywords": "FastAPI"})
    assert len(disc_out.opportunities) > 0

    matcher = MatchingAgent(llm_service)
    match_out = matcher.run({"skills": ["Python"]}, {"title": "Backend Engineer"})
    assert match_out.skill_match > 0

    researcher = ResearchAgent(llm_service)
    res_out = researcher.run("Stripe")
    assert res_out.overall_fit >= 80.0

    personalization = ResumePersonalizationAgent(llm_service)
    pers_out = personalization.run({"skills": ["FastAPI", "PostgreSQL"]}, {"company_name": "Stripe", "title": "Backend Engineer"})
    assert pers_out.evidence_validation_passed is True
    assert "Stripe" in pers_out.cover_letter_text


def test_human_approval_gateway_routing():
    llm_service = LLMService()
    orchestrator = OpportunityGraphOrchestrator(llm_service)

    # Route pending approval
    route_pending = orchestrator._route_approval({"approval_status": "PENDING"})
    assert route_pending == "pending"

    # Route approved
    route_approved = orchestrator._route_approval({"approval_status": "APPROVED"})
    assert route_approved == "approved"

    # Route rejected
    route_rejected = orchestrator._route_approval({"approval_status": "REJECTED"})
    assert route_rejected == "rejected"
