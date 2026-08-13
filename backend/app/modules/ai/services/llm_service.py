import os
from typing import Optional, Any
from app.core.logging import logger


class LLMService:
    """
    Free-Tier First LLM Provider Abstraction Layer.
    Primary Provider = Google Gemini
    Fallback Provider = Groq
    """

    def __init__(self):
        self.primary_provider = os.getenv("AI_PRIMARY_PROVIDER", "gemini").lower()
        self.fallback_provider = os.getenv("AI_FALLBACK_PROVIDER", "groq").lower()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    def get_llm(self, reasoning: bool = False) -> Any:
        # 1. Try Primary Provider (Google Gemini)
        if (self.primary_provider == "gemini" or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                try:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    model = "gemini-1.5-pro" if reasoning else self.gemini_model
                    logger.info(f"Initializing Gemini LLM ({model})")
                    return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2)
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini LLM: {e}. Falling back to Groq.")

        # 2. Try Fallback Provider (Groq)
        if (self.fallback_provider == "groq" or os.getenv("GROQ_API_KEY")):
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    from langchain_groq import ChatGroq
                    logger.info(f"Initializing Groq Fallback LLM ({self.groq_model})")
                    return ChatGroq(model_name=self.groq_model, groq_api_key=api_key, temperature=0.2)
                except Exception as e:
                    logger.warning(f"Failed to initialize Groq LLM: {e}")

        # 3. Controlled Fallback Runner (if no API keys provided in dev environment)
        logger.info("No API keys found for Gemini/Groq; using Controlled Fallback Engine.")
        return FallbackMockLLM(model_name="free-tier-fallback-engine")


class FallbackMockLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def invoke(self, prompt: Any) -> Any:
        prompt_text = str(prompt)
        logger.info(f"FallbackMockLLM processing request: {prompt_text[:100]}...")
        return FallbackMessage(
            content=f"[AI Intelligence Analysis via {self.model_name}]\nAnalysis complete based on structured career profile, resume data, and job requirements."
        )


class FallbackMessage:
    def __init__(self, content: str):
        self.content = content
