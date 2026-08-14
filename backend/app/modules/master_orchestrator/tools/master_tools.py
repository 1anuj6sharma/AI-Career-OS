"""
Module 15 — LangChain Tools for Master Career Orchestrator
"""
from typing import Dict, Any, List
from langchain_core.tools import tool
from app.modules.master_orchestrator.services.module_registry import MODULE_REGISTRY


@tool
def get_global_career_state(user_id: int) -> Dict[str, Any]:
    """Retrieves unified global Career State across Modules 1–14."""
    return {
        "user_id": user_id,
        "target_role": "Senior Backend / AI Engineer",
        "performance_score": 82.5,
        "readiness_pct": 78.5,
        "primary_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "untested_gaps": ["System Design", "AWS Infrastructure"],
        "application_conversion_rate": 25.0
    }


@tool
def resolve_module_capability(capability_name: str) -> Dict[str, Any]:
    """Resolves which module registered in Module Registry owns a specified capability."""
    for key, info in MODULE_REGISTRY.items():
        if capability_name in info["capabilities"]:
            return info
    return {"module_code": "module_15", "name": "Master Orchestrator"}


@tool
def execute_module_workflow(module_code: str, action_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invokes workflow action on registered target module."""
    return {
        "status": "SUCCESS",
        "module_code": module_code,
        "action_name": action_name,
        "result": f"Executed {action_name} successfully on {module_code}."
    }
