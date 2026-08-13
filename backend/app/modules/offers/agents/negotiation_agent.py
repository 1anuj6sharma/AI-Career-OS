from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService


class NegotiationAgent:
    """
    Agent 6: AI Negotiation Agent
    Evaluates negotiation leverage and generates negotiation email drafts requiring human review and approval.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        company_name: str,
        role: str,
        current_base: float,
        target_base: float,
        leverage_score: float = 80.0,
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Compensation Negotiator.
        Draft a polite, professional counter-offer email to increase fixed base salary:

        Company: {company_name}
        Role: {role}
        Offered Base: ₹{current_base / 100000:.1f} LPA
        Target Base: ₹{target_base / 100000:.1f} LPA
        Negotiation Leverage Score: {leverage_score}/100

        Draft a compelling ask emphasizing candidate backend microservice experience and role fit.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        email_body = (
            f"Dear Recruiting Team @ {company_name},\n\n"
            f"Thank you very much for extending the offer for the {role} position. "
            f"I am extremely excited about the prospect of joining {company_name} and contributing to your backend platform engineering team.\n\n"
            f"Given my hands-on experience designing high-throughput Python and FastAPI microservices, I would like to discuss if there is flexibility in the fixed base compensation towards ₹{target_base / 100000:.1f} LPA.\n\n"
            f"I look forward to discussing this further.\n\nBest regards,\nCandidate"
        )

        return {
            "agent": "NegotiationAgent",
            "target_compensation": target_base,
            "minimum_compensation": current_base,
            "leverage_score": leverage_score,
            "primary_ask": f"Increase base salary from ₹{current_base / 100000:.1f} LPA to ₹{target_base / 100000:.1f} LPA",
            "secondary_ask": "One-time joining bonus if base salary budget is fixed",
            "fallback_ask": "Early performance and salary review at 6 months",
            "draft_negotiation_email": getattr(response, "content", email_body),
        }
