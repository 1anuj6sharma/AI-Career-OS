from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService
from app.modules.learning.tools.learning_tools import search_learning_rag_docs


class TutorAgent:
    """
    Agent 3: AI Tutor Agent
    Answers technical questions using grounded RAG documentation retrieval tailored to candidate mode (Beginner, Intermediate, Advanced, Interview).
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, topic: str, question: str, mode: str = "INTERMEDIATE") -> Dict[str, Any]:
        # 1. Grounded Vector RAG Retrieval
        rag_docs = search_learning_rag_docs(topic, question)

        prompt = f"""
        Act as a Principal AI Technical Tutor operating in '{mode}' mode.

        Topic: {topic}
        User Question: "{question}"
        Retrieved Grounded RAG Documentation:
        {rag_docs}

        Explain clearly, provide a clean code example if applicable, and suggest a practical exercise.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "TutorAgent",
            "topic": topic,
            "explanation": getattr(response, "content", str(response)),
            "retrieved_docs_count": len(rag_docs),
            "suggested_practice": f"Build a mini {topic} setup and inspect logs",
            "code_example": f"# {topic} Example\nimport os\nprint('Configured {topic}')",
        }
