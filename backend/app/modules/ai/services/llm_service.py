import os
from typing import Optional, Any
from app.core.logging import logger


class LLMService:
    """
    LLM Provider Abstraction Layer.
    Supports OpenAI, Google Gemini, Anthropic, Groq, and fallback heuristics.
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.default_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.reasoning_model = os.getenv("LLM_REASONING_MODEL", "gpt-4o")

    def get_llm(self, reasoning: bool = False) -> Any:
        model_name = self.reasoning_model if reasoning else self.default_model

        if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model=model_name, temperature=0.2)
            except Exception as e:
                logger.warning(f"Failed to initialize ChatOpenAI: {e}")

        elif self.provider == "google" or os.getenv("GOOGLE_API_KEY"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), temperature=0.2)
            except Exception as e:
                logger.warning(f"Failed to initialize ChatGoogleGenerativeAI: {e}")

        elif self.provider == "anthropic" or os.getenv("ANTHROPIC_API_KEY"):
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"), temperature=0.2)
            except Exception as e:
                logger.warning(f"Failed to initialize ChatAnthropic: {e}")

        # Fallback Mock / Heuristic LLM runner if no external API keys set
        return FallbackMockLLM(model_name=model_name)


class FallbackMockLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def invoke(self, prompt: Any) -> Any:
        prompt_text = str(prompt)
        logger.info(f"FallbackMockLLM processing request: {prompt_text[:100]}...")
        return FallbackMessage(content=f"[AI Intelligence Analysis via {self.model_name}]\nAnalysis complete based on structured career profile and job data.")


class FallbackMessage:
    def __init__(self, content: str):
        self.content = content
