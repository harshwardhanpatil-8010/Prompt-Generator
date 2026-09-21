from typing import Dict
from pydantic import BaseModel
from .graph import DependencyGraphData
from .representation import (
    ContextSource,
    RequirementCategory,
    RequirementPriority,
    StructuredContext,
)


class ContextScores(BaseModel):
    id: str
    relevance: float = 0.0
    importance: float = 0.0
    redundancy: float = 0.0
    dependency_score: float = 0.0
    confidence: float = 0.0
    prune_decision: str = "KEEP"  # KEEP, PRUNE, COMPRESS
    prune_reason: str = ""


class ContextEvaluator:
    """Heuristic scoring system computing relevance, redundancy, importance, and dependency depth."""

    def evaluate(
        self, ctx: StructuredContext, graph: DependencyGraphData
    ) -> Dict[str, ContextScores]:
        scores: Dict[str, ContextScores] = {}
        critical_nodes = set(graph.critical_path_node_ids)
        isolated_nodes = set(graph.isolated_node_ids)

        for req in ctx.requirements:
            is_critical = (
                req.priority == RequirementPriority.HIGH.value
                or req.id in critical_nodes
                or req.category in [
                    RequirementCategory.SECURITY.value,
                    RequirementCategory.ACCESSIBILITY.value,
                ]
            )
            is_user_source = req.source == ContextSource.USER.value
            is_low_priority = req.priority == RequirementPriority.LOW.value
            is_isolated = req.id in isolated_nodes

            if is_low_priority and is_isolated:
                relevance = 0.25
                importance = 0.20
                redundancy = 0.85
                dep_score = 0.05
                conf = req.confidence
                prune = "PRUNE"
                reason = "Isolated low-priority non-functional item with no dependent components or APIs."
            elif is_critical:
                relevance = 0.98 if is_user_source else 0.92
                importance = 0.95
                redundancy = 0.05
                dep_score = 0.90
                conf = req.confidence
                prune = "KEEP"
                reason = "High-priority functional or security requirement on the critical dependency path."
            elif req.priority == RequirementPriority.MEDIUM.value:
                relevance = 0.85
                importance = 0.75
                redundancy = 0.20
                dep_score = 0.60
                conf = req.confidence
                prune = "COMPRESS"
                reason = "Important functional feature; condensed to dense technical constraint."
            else:
                relevance = 0.70
                importance = 0.50
                redundancy = 0.40
                dep_score = 0.40
                conf = req.confidence
                prune = "KEEP"
                reason = "Supporting requirement."

            scores[req.id] = ContextScores(
                id=req.id,
                relevance=relevance,
                importance=importance,
                redundancy=redundancy,
                dependency_score=dep_score,
                confidence=conf,
                prune_decision=prune,
                prune_reason=reason,
            )

        return scores
