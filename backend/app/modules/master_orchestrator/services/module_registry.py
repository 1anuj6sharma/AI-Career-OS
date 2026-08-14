"""
Module 15 — Capability-Based Module Registry
Maps high-level capabilities to Modules 1–14 without hardcoding route strings.
"""
from typing import Dict, Any, List, Optional

MODULE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "profile": {
        "module_code": "module_2",
        "name": "User Profile & Skill Intelligence",
        "capabilities": ["candidate_profile", "skill_inventory", "education", "experience_history"],
        "api_prefix": "/api/v1/profile"
    },
    "jobs": {
        "module_code": "module_3",
        "name": "Job Application Tracker",
        "capabilities": ["application_tracking", "application_checklist", "job_logs"],
        "api_prefix": "/api/v1/jobs"
    },
    "resumes": {
        "module_code": "module_5",
        "name": "Resume Intelligence & Builder",
        "capabilities": ["resume_builder", "ats_analysis", "resume_tailoring", "cover_letter_generation"],
        "api_prefix": "/api/v1/resumes"
    },
    "interviews": {
        "module_code": "module_6",
        "name": "Interview Intelligence & Prep",
        "capabilities": ["mock_interview", "question_bank", "interview_analysis", "feedback_evaluation"],
        "api_prefix": "/api/v1/interviews"
    },
    "career": {
        "module_code": "module_7",
        "name": "Career Roadmap & Execution Engine",
        "capabilities": ["roadmap_generation", "milestone_tracking", "roadmap_adaptation"],
        "api_prefix": "/api/v1/career"
    },
    "learning": {
        "module_code": "module_8",
        "name": "Learning Hub & Skill Development",
        "capabilities": ["skill_gap_course", "learning_path", "skill_quiz", "knowledge_assessment"],
        "api_prefix": "/api/v1/learning"
    },
    "brand": {
        "module_code": "module_9",
        "name": "Portfolio & Brand Engineering",
        "capabilities": ["portfolio_showcase", "github_brand_score", "case_study_generator"],
        "api_prefix": "/api/v1/brand"
    },
    "opportunities": {
        "module_code": "module_10",
        "name": "Job Matching & Opportunity Intelligence",
        "capabilities": ["opportunity_scoring", "company_research", "readiness_evaluation"],
        "api_prefix": "/api/v1/opportunities"
    },
    "network": {
        "module_code": "module_11",
        "name": "Networking & Referral CRM",
        "capabilities": ["contacts_crm", "referral_outreach", "networking_log"],
        "api_prefix": "/api/v1/network"
    },
    "offers": {
        "module_code": "module_12",
        "name": "Offer Management & Decision Matrix",
        "capabilities": ["offer_comparison", "compensation_matrix", "decision_evaluation"],
        "api_prefix": "/api/v1/offers"
    },
    "career_performance": {
        "module_code": "module_13",
        "name": "Career Performance & Growth Engine",
        "capabilities": ["productivity_score", "skill_progress_matrix", "weekly_review", "risk_detection", "scenario_simulation"],
        "api_prefix": "/api/v1/career"
    },
    "opportunity_acquisition": {
        "module_code": "module_14",
        "name": "Opportunity Acquisition Engine",
        "capabilities": ["job_discovery", "deduplication", "human_approval_gateway", "application_handoff", "conversion_analytics"],
        "api_prefix": "/api/v1/opportunities"
    }
}


def resolve_modules_for_capabilities(capabilities: List[str]) -> List[Dict[str, Any]]:
    """Resolves matching module descriptors for a list of target capabilities."""
    matched = []
    for cap in capabilities:
        for key, info in MODULE_REGISTRY.items():
            if cap in info["capabilities"] and info not in matched:
                matched.append(info)
    return matched
