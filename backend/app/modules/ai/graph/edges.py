from app.modules.ai.graph.state import CareerGraphState


def route_by_intent(state: CareerGraphState) -> str:
    return state.get("intent", "career")
