"""
Unit & Integration Tests for Module 16 — AI Career Network, Personal Brand & Referral Intelligence Engine
"""
import pytest
from app.modules.network.services.referral_intelligence_service import ReferralIntelligenceService
from app.modules.ai.services.llm_service import LLMService
from app.modules.network.agents.networking_agents import (
    NetworkingSupervisorAgent,
    ContactDiscoveryAgent,
    RelationshipIntelligenceAgent,
    ReferralAgent,
    OutreachAgent,
    PersonalBrandAgent,
    FollowupAgent,
)
from app.modules.network.graph.networking_graph import NetworkingGraphOrchestrator


def test_referral_score_calculation():
    service = ReferralIntelligenceService(repo=None)
    scores = service.calculate_referral_score(
        relationship_strength=85.0,
        company_relevance=95.0,
        role_alignment=90.0,
        interaction_recency_days=5
    )

    assert "referral_score" in scores
    assert scores["referral_score"] > 80.0
    assert scores["relevance_score"] == 95.0


def test_grounded_outreach_generation():
    service = ReferralIntelligenceService(repo=None)
    outreach = service.generate_grounded_outreach(
        contact_name="Siddharth Mehta",
        contact_company="Stripe",
        contact_role="Engineering Manager",
        verified_evidence=["FastAPI microservices", "Async PGVector", "Redis Caching"]
    )

    assert "Stripe" in outreach["subject"]
    assert "FastAPI microservices" in outreach["message"]
    assert "Anuj Saraswat" in outreach["message"]


def test_networking_agents_suite():
    llm_service = LLMService()

    discovery = ContactDiscoveryAgent(llm_service)
    disc_out = discovery.run("Stripe", "Senior Backend Engineer")
    assert len(disc_out.discovered_contacts) > 0

    rel_agent = RelationshipIntelligenceAgent(llm_service)
    rel_out = rel_agent.run("Siddharth Mehta", "Stripe")
    assert rel_out.referral_potential > 80.0

    outreach_agent = OutreachAgent(llm_service)
    out_msg = outreach_agent.run(1, "Siddharth Mehta", "Stripe", ["FastAPI"])
    assert out_msg.human_approval_required is True
    assert "Stripe" in out_msg.message

    brand_agent = PersonalBrandAgent(llm_service)
    brand_out = brand_agent.run(1)
    assert brand_out.brand_score >= 80.0


def test_networking_langgraph_orchestrator():
    llm_service = LLMService()
    orchestrator = NetworkingGraphOrchestrator(llm_service)

    route_approved = orchestrator._route_approval({"approval_status": "APPROVED"})
    assert route_approved == "approved"

    route_pending = orchestrator._route_approval({"approval_status": "PENDING"})
    assert route_pending == "pending"
