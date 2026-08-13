from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.modules.ai.models import AIConversation, AIMessage


def get_conversation_history(db: Session, conversation_id: int) -> List[Dict[str, str]]:
    messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at.asc())
        .all()
    )
    return [{"sender": m.sender, "content": m.content} for m in messages]


def add_message_to_conversation(db: Session, conversation_id: int, sender: str, content: str) -> AIMessage:
    msg = AIMessage(conversation_id=conversation_id, sender=sender, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
