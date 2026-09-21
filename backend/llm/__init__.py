from ..config import settings
from .base import BaseLLMProvider
from .mock import MockLLMProvider
from .ollama import OllamaLLMProvider


def get_llm_provider(provider_type: str = None) -> BaseLLMProvider:
    provider = (provider_type or settings.LLM_PROVIDER).lower().strip()
    if provider == "ollama":
        return OllamaLLMProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
        )
    return MockLLMProvider()


__all__ = ["BaseLLMProvider", "MockLLMProvider", "OllamaLLMProvider", "get_llm_provider"]
