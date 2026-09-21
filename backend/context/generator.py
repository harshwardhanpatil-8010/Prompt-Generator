from typing import Optional
from ..llm.base import BaseLLMProvider
from .representation import StructuredContext, WebpageContext


class ContextGenerator:
    """Generates structured, multi-dimensional context from user requirements and optional webpage inputs."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider

    def generate(
        self, prompt: str, webpage_context: Optional[WebpageContext] = None
    ) -> StructuredContext:
        # Extract intent & domain variables
        intent = self.llm.extract_intent(prompt, webpage_context)

        # Expand requirements with explicit source labeling
        requirements = self.llm.expand_requirements(intent, prompt, webpage_context)

        # Build full structured representation
        ctx = self.llm.generate_specification(intent, requirements, prompt, webpage_context)
        return ctx
