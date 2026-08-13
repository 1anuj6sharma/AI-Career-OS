from typing import Dict, Any
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from app.modules.ai.graph.state import CareerGraphState
from app.modules.ai.graph.nodes import classify_intent_node, execute_agent_node
from app.modules.ai.services.llm_service import LLMService


class CareerGraphOrchestrator:
    """
    LangGraph Workflow Engine for AI Career OS.
    Orchestrates intent classification, multi-agent execution, tool calls, and state management.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CareerGraphState)

        def classify_step(state: CareerGraphState):
            return classify_intent_node(state, self.llm_service)

        builder.add_node("classify_intent", classify_step)
        builder.set_entry_point("classify_intent")

        return builder

    def run(self, db: Session, user_id: int, user_request: str, job_id: int = None) -> Dict[str, Any]:
        initial_state: CareerGraphState = {
            "user_id": user_id,
            "user_request": user_request,
            "job_id": job_id,
            "agent_results": {},
            "tool_results": [],
            "pending_actions": [],
            "final_response": "",
        }

        # 1. Intent classification step
        state = classify_intent_node(initial_state, self.llm_service)

        # 2. Execute multi-agent node
        state = execute_agent_node(state, db, self.llm_service)

        return {
            "intent": state.get("intent"),
            "final_response": state.get("final_response"),
            "agent_results": state.get("agent_results"),
            "pending_actions": state.get("pending_actions"),
        }
