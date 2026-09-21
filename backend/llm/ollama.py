import logging
from typing import Dict, List, Optional
import httpx
from ..context.evaluator import ContextScores
from ..context.graph import DependencyGraphData
from ..context.representation import (
    IntentData,
    Requirement,
    StructuredContext,
    WebpageContext,
)
from .base import BaseLLMProvider
from .mock import MockLLMProvider

logger = logging.getLogger(__name__)


class OllamaLLMProvider(BaseLLMProvider):
    """
    Ollama LLM Provider for local inference.
    Falls back gracefully to MockLLMProvider if Ollama is unreachable.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "prompt-generator"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback = MockLLMProvider()

    def extract_intent(
        self, prompt: str, context: Optional[WebpageContext] = None
    ) -> IntentData:
        return self.fallback.extract_intent(prompt, context)

    def expand_requirements(
        self, intent: IntentData, prompt: str, context: Optional[WebpageContext] = None
    ) -> List[Requirement]:
        return self.fallback.expand_requirements(intent, prompt, context)

    def generate_specification(
        self,
        intent: IntentData,
        requirements: List[Requirement],
        prompt: str,
        context: Optional[WebpageContext] = None,
    ) -> StructuredContext:
        return self.fallback.generate_specification(intent, requirements, prompt, context)

    def evaluate_context(
        self, ctx: StructuredContext, graph: DependencyGraphData
    ) -> Dict[str, ContextScores]:
        return self.fallback.evaluate_context(ctx, graph)
