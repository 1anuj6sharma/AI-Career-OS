from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.models import AIMemory


def save_long_term_fact(db: Session, user_id: int, key: str, value: str, memory_type: str = "PREFERENCE") -> AIMemory:
    mem = db.query(AIMemory).filter(AIMemory.user_id == user_id, AIMemory.key == key).first()
    if mem:
        mem.value = value
    else:
        mem = AIMemory(user_id=user_id, memory_type=memory_type, key=key, value=value)
        db.add(mem)

    db.commit()
    db.refresh(mem)
    return mem


def get_user_long_term_memories(db: Session, user_id: int) -> Dict[str, str]:
    memories = db.query(AIMemory).filter(AIMemory.user_id == user_id).all()
    return {m.key: m.value for m in memories}
