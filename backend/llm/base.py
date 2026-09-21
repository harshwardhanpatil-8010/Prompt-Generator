from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from ..context.evaluator import ContextScores
from ..context.graph import DependencyGraphData
from ..context.representation import (
    IntentData,
    Requirement,
    StructuredContext,
    WebpageContext,
)


class BaseLLMProvider(ABC):
    """Abstract interface for LLM operations in the context-engineering pipeline."""

    @abstractmethod
    def extract_intent(
        self, prompt: str, context: Optional[WebpageContext] = None
    ) -> IntentData:
        """Extract structured intent from a user's raw requirement and optional webpage context."""
        pass

    @abstractmethod
    def expand_requirements(
        self, intent: IntentData, prompt: str, context: Optional[WebpageContext] = None
    ) -> List[Requirement]:
        """Expand user intent into a structured list of prioritized functional & non-functional requirements."""
        pass

    @abstractmethod
    def generate_specification(
        self,
        intent: IntentData,
        requirements: List[Requirement],
        prompt: str,
        context: Optional[WebpageContext] = None,
    ) -> StructuredContext:
        """Generate full structured context representation (Pages, Components, APIs, DB, Tasks, Design, Tech)."""
        pass

    @abstractmethod
    def evaluate_context(
        self, ctx: StructuredContext, graph: DependencyGraphData
    ) -> Dict[str, ContextScores]:
        """Evaluate context elements for relevance, importance, redundancy, and dependency depth."""
        pass
