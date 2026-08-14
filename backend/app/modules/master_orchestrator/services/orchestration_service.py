"""
Module 15 — Master Orchestration Service
Contains Next Best Action Engine, Goal Decomposition, 3-Level Memory, and Adaptive Strategy logic.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.master_orchestrator.repository import MasterOrchestratorRepository
from app.modules.master_orchestrator.models import (
    MasterCareerPlan,
    MasterPlanStep,
    MasterCareerDecision,
    MasterCareerEvent,
    MasterCareerMemory,
    MasterCareerStrategy,
    MasterApprovalRecord,
)
from app.modules.master_orchestrator.services.module_registry import resolve_modules_for_capabilities


class MasterOrchestrationService:
    def __init__(self, repo: MasterOrchestratorRepository):
        self.repo = repo

    # ------------------------------------------------------------------------
    # 1. Deterministic Next Best Action Engine
    # ------------------------------------------------------------------------
    def calculate_next_best_action(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calculates the single highest-value action for the user using deterministic scoring:
        Rank Score = (0.3 * Impact) + (0.25 * Alignment) + (0.2 * Urgency) + (0.15 * OppValue) - (0.1 * Effort)
        """
        # Query active goals and metrics
        active_plan = self.repo.get_active_plan(user_id)
        
        # Candidate actions evaluation matrix
        candidates = [
            {
                "action_title": "Complete System Design Mock Interview",
                "description": "Your current target role requires stronger system design performance, which is your largest gap.",
                "category": "INTERVIEW_PREP",
                "target_module": "module_6",
                "impact": 95.0,
                "alignment": 90.0,
                "urgency": 85.0,
                "opp_value": 80.0,
                "effort": 30.0,
            },
            {
                "action_title": "Review & Approve Stripe Senior Backend Engineer Application",
                "description": "High match opportunity (91.5/100 score) is prepared and awaiting your human approval.",
                "category": "OPPORTUNITY_ACQUISITION",
                "target_module": "module_14",
                "impact": 90.0,
                "alignment": 95.0,
                "urgency": 90.0,
                "opp_value": 95.0,
                "effort": 10.0,
            },
            {
                "action_title": "Complete Azure Data Factory Containerization Course",
                "description": "Required skill gap for cloud data pipeline roles.",
                "category": "LEARNING",
                "target_module": "module_8",
                "impact": 80.0,
                "alignment": 85.0,
                "urgency": 70.0,
                "opp_value": 75.0,
                "effort": 45.0,
            }
        ]

        # Rank deterministically
        for cand in candidates:
            score = (
                (0.30 * cand["impact"]) +
                (0.25 * cand["alignment"]) +
                (0.20 * cand["urgency"]) +
                (0.15 * cand["opp_value"]) -
                (0.10 * cand["effort"])
            )
            cand["rank_score"] = round(score, 1)

        sorted_cands = sorted(candidates, key=lambda x: x["rank_score"], reverse=True)
        winner = sorted_cands[0]

        return {
            "action_title": winner["action_title"],
            "description": winner["description"],
            "category": winner["category"],
            "target_module": winner["target_module"],
            "expected_impact": "HIGH" if winner["impact"] >= 90 else "MEDIUM",
            "rank_score": winner["rank_score"],
            "execution_payload": {"target_module": winner["target_module"]}
        }

    # ------------------------------------------------------------------------
    # 2. Master Strategy Management (Versioned Active Strategy)
    # ------------------------------------------------------------------------
    def get_or_create_active_strategy(self, user_id: int, goal_title: str = "Senior Backend / AI Engineer") -> MasterCareerStrategy:
        active = self.repo.get_active_strategy(user_id)
        if active:
            return active

        new_strat = MasterCareerStrategy(
            user_id=user_id,
            version_number=1,
            strategy_title=f"Mastery Plan v1 for {goal_title}",
            objective=f"Systematically master backend microservices, system design, and AI application engineering.",
            reasons_for_pivot="Initial master career baseline strategy created.",
            is_active=True
        )
        return self.repo.create_strategy(new_strat)

    def adapt_strategy(self, user_id: int, pivot_reason: str, new_objective: str) -> MasterCareerStrategy:
        active = self.repo.get_active_strategy(user_id)
        current_ver = active.version_number if active else 1
        new_ver = current_ver + 1

        new_strat = MasterCareerStrategy(
            user_id=user_id,
            version_number=new_ver,
            strategy_title=f"Mastery Strategy v{new_ver}",
            objective=new_objective,
            reasons_for_pivot=pivot_reason,
            is_active=True
        )
        return self.repo.create_strategy(new_strat)

    # ------------------------------------------------------------------------
    # 3. 3-Level Career Memory Management
    # ------------------------------------------------------------------------
    def save_career_memory(self, user_id: int, memory_type: str, key: str, content: Dict[str, Any]) -> MasterCareerMemory:
        mem = MasterCareerMemory(
            user_id=user_id,
            memory_type=memory_type,
            key=key,
            content_json=content
        )
        return self.repo.save_memory(mem)

    # ------------------------------------------------------------------------
    # 4. Master Plan & Goal Decomposition
    # ------------------------------------------------------------------------
    def decompose_and_create_master_plan(self, user_id: int, goal_title: str) -> MasterCareerPlan:
        strategy = self.get_or_create_active_strategy(user_id, goal_title)

        plan = MasterCareerPlan(
            user_id=user_id,
            goal_title=goal_title,
            strategy_summary=strategy.objective,
            status="ACTIVE",
            version=strategy.version_number
        )
        created_plan = self.repo.create_plan(plan)

        # Decomposed step DAG across modules
        steps_data = [
            {
                "module_name": "module_8",
                "action_name": "FastAPI & System Design Knowledge Assessment",
                "priority": 1,
                "dependencies": []
            },
            {
                "module_name": "module_5",
                "action_name": "Optimize Resume for Senior Backend & AI Engineer roles",
                "priority": 2,
                "dependencies": ["module_8"]
            },
            {
                "module_name": "module_14",
                "action_name": "Discover & Evaluate High Match Opportunities (>90 Score)",
                "priority": 3,
                "dependencies": ["module_5"]
            },
            {
                "module_name": "module_6",
                "action_name": "Conduct System Design & Architecture Mock Interview",
                "priority": 4,
                "dependencies": ["module_14"]
            }
        ]

        for step in steps_data:
            s_obj = MasterPlanStep(
                plan_id=created_plan.id,
                module_name=step["module_name"],
                action_name=step["action_name"],
                priority=step["priority"],
                status="PENDING",
                dependencies_json=step["dependencies"]
            )
            self.repo.create_plan_step(s_obj)

        logger.info(f"Decomposed and created master plan id={created_plan.id} for user={user_id}")
        return self.repo.get_active_plan(user_id)

    # ------------------------------------------------------------------------
    # 5. Command Center Dashboard Aggregator
    # ------------------------------------------------------------------------
    def get_command_center_dashboard(self, db: Session, user_id: int) -> Dict[str, Any]:
        strategy = self.get_or_create_active_strategy(user_id)
        next_action = self.calculate_next_best_action(db, user_id)
        active_plan = self.repo.get_active_plan(user_id)
        pending_apps = self.repo.list_pending_approvals(user_id)
        events = self.repo.list_events(user_id)

        return {
            "user_id": user_id,
            "current_goal": strategy.strategy_title,
            "current_strategy": strategy,
            "next_best_action": next_action,
            "career_readiness_pct": 78.5,
            "performance_score": 82.5,
            "active_plan": active_plan,
            "pending_approvals": pending_apps,
            "active_risks_count": 1,
            "top_opportunities_count": 8,
            "recent_events_count": len(events)
        }
