from typing import Dict, Any, List
from app.modules.ai.services.llm_service import LLMService
from app.modules.network.tools.network_tools import search_networking_rag_documents


class OutreachAgent:
    """
    Agent 3: AI Outreach Generator Agent
    Generates personalized outreach drafts (Connection Request, Recruiter Outreach, Referral Request) grounded in profile & project evidence using LangChain.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(
        self,
        user_id: int,
        contact_name: str,
        contact_role: str,
        company_name: str,
        purpose: str = "RECRUITER_OUTREACH",
        opportunity_title: str = "Senior Backend Engineer",
    ) -> Dict[str, Any]:
        # Grounded RAG Retrieval
        evidence = search_networking_rag_documents(user_id, company_name)

        prompt = f"""
        Act as a Professional Recruiter Communications Specialist.
        Draft a high-converting, personalized outreach message:

        Recipient: {contact_name} ({contact_role} @ {company_name})
        Purpose: {purpose}
        Target Opportunity: {opportunity_title}
        Grounded User Evidence: {evidence}

        Rules:
        - Concise, professional, and respectful.
        - Grounded in real project evidence. Do NOT invent fake experience.
        - Require user approval before sending.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        subject = f"Exploring {opportunity_title} opportunities at {company_name}" if "OUTREACH" in purpose else f"Connecting re: {opportunity_title}"
        body = (
            f"Hi {contact_name},\n\n"
            f"I hope you're doing well. I noticed your work leading engineering recruitment at {company_name}. "
            f"As a Backend Engineer specializing in Python, FastAPI, and Docker microservice architectures, I've followed {company_name}'s recent technical initiatives with great interest.\n\n"
            f"I'd love to connect and learn if my background aligns with open {opportunity_title} roles on your team.\n\n"
            f"Best regards,\nCandidate"
        )

        return {
            "agent": "OutreachAgent",
            "purpose": purpose,
            "subject": subject,
            "message": getattr(response, "content", body),
            "evidence_used": evidence,
        }
