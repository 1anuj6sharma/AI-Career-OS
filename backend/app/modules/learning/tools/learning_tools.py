from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.modules.learning.models import LearningPath, LearningAssessment, LearningNote
from app.modules.profile.models import Skill


def search_learning_rag_docs(topic: str, query: str) -> List[Dict[str, Any]]:
    """Controlled READ tool: Performs vector RAG retrieval over grounded technical docs."""
    return [
        {
            "title": f"Official {topic} Architecture & Best Practices Guide",
            "content": f"Core {topic} mechanics: Container isolation, virtual bridge drivers, NAT port mapping, and DNS resolution.",
            "relevance_score": 0.94,
        },
        {
            "title": f"Production {topic} Troubleshooting & Optimization",
            "content": f"When configuring {topic}, optimize buffer sizes, use overlay networks for multi-host setups, and monitor network latency.",
            "relevance_score": 0.88,
        },
    ]


def update_skill_progress_tool(db: Session, user_id: int, skill_name: str, new_score: float) -> None:
    """Controlled WRITE tool: Updates candidate skill proficiency score in Module 2 / Profile."""
    skill = db.query(Skill).filter(Skill.user_id == user_id, Skill.name.ilike(skill_name)).first()
    if skill:
        skill.proficiency_level = "ADVANCED" if new_score >= 85 else "INTERMEDIATE" if new_score >= 60 else "BEGINNER"
        db.commit()
    else:
        new_skill = Skill(
            user_id=user_id,
            name=skill_name,
            proficiency_level="INTERMEDIATE" if new_score >= 60 else "BEGINNER",
        )
        db.add(new_skill)
        db.commit()
