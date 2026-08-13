from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService
from app.modules.brand.tools.brand_tools import search_brand_rag_documents


class ContentAgent:
    """
    Agent 5: AI Content Agent
    Generates technical articles, LinkedIn posts, project announcements, and READMEs grounded in Personal Brand RAG evidence.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, user_id: int, content_type: str, topic: str) -> Dict[str, Any]:
        # Grounded RAG Retrieval
        rag_evidence = search_brand_rag_documents(user_id, topic)

        prompt = f"""
        Act as a Principal Technical Content Writer.
        Generate a professional {content_type} grounded strictly in user project evidence:

        Target Topic: "{topic}"
        User Project Evidence: {rag_evidence}

        Generate publication-ready content. Do NOT invent fake metrics or experience.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ContentAgent",
            "content_type": content_type,
            "title": f"Technical Article: {topic}",
            "content": getattr(response, "content", str(response)),
            "evidence_used": rag_evidence,
        }
