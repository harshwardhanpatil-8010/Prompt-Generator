from typing import Any, Dict, List, Tuple
from .evaluator import ContextScores
from .graph import DependencyGraphData
from .representation import (
    ContextSource,
    ContextStatus,
    Requirement,
    RequirementCategory,
    RequirementPriority,
    StructuredContext,
)
from .token_counter import OptimizationMetrics, TokenCounter


class ContextOptimizer:
    """
    Optimizes context representation by pruning redundant/low-value nodes,
    compressing descriptions, and enforcing 100% preservation of critical requirements.
    """

    def optimize(
        self,
        ctx: StructuredContext,
        graph: DependencyGraphData,
        evaluation_scores: Dict[str, ContextScores],
    ) -> Tuple[Dict[str, Any], OptimizationMetrics, List[Requirement]]:
        pruned_item_ids: List[str] = []
        compressed_item_ids: List[str] = []
        preserved_requirements: List[Requirement] = []

        critical_nodes = set(graph.critical_path_node_ids)

        # 1. Optimize Requirements
        dense_reqs = []
        for req in ctx.requirements:
            score = evaluation_scores.get(req.id)
            is_critical = (
                req.priority == RequirementPriority.HIGH.value
                or req.id in critical_nodes
                or req.category in [
                    RequirementCategory.SECURITY.value,
                    RequirementCategory.ACCESSIBILITY.value,
                ]
                or req.source == ContextSource.USER.value
            )

            # Never prune critical requirements
            if is_critical or (score and score.prune_decision != "PRUNE"):
                clean_desc = req.description.strip()
                if score and score.prune_decision == "COMPRESS":
                    compressed_item_ids.append(req.id)

                preserved_req = Requirement(
                    id=req.id,
                    title=req.title,
                    description=clean_desc,
                    category=req.category,
                    priority=req.priority,
                    source=req.source,
                    confidence=req.confidence,
                    status=ContextStatus.APPROVED.value,
                    dependencies=req.dependencies,
                    related_pages=req.related_pages,
                    related_components=req.related_components,
                    related_apis=req.related_apis,
                    related_entities=req.related_entities,
                )
                preserved_requirements.append(preserved_req)

                dense_reqs.append({
                    "id": req.id,
                    "title": req.title,
                    "priority": req.priority,
                    "spec": clean_desc,
                })
            else:
                pruned_item_ids.append(req.id)

        # 2. Compact Pages and Components
        optimized_pages = [
            {
                "name": p.name,
                "path": p.path,
                "sections": p.sections,
            }
            for p in ctx.pages
            if p.status != ContextStatus.REJECTED.value
        ]

        optimized_components = [
            {
                "name": c.name,
                "type": c.type,
                "props": c.props,
            }
            for c in ctx.components
            if c.status != ContextStatus.REJECTED.value
        ]

        optimized_apis = [
            {
                "endpoint": f"{a.method} {a.endpoint}",
                "desc": a.description,
            }
            for a in ctx.apis
            if a.status != ContextStatus.REJECTED.value
        ]

        optimized_entities = [
            {
                "entity": e.name,
                "fields": [f["name"] for f in e.fields],
            }
            for e in ctx.database_entities
            if e.status != ContextStatus.REJECTED.value
        ]

        # 3. Dense Design & Technical tokens
        dense_design = {
            "style": ctx.design.visual_style,
            "theme": ctx.design.color_direction,
            "typography": ctx.design.typography,
            "layout": ctx.design.layout,
            "responsive": ctx.design.responsive_behavior,
            "nav": ctx.design.navigation,
        }

        dense_technical = {
            "stack": ctx.technical.frontend,
            "api_style": ctx.technical.api_style,
            "security": ctx.technical.security,
            "accessibility": ctx.technical.accessibility,
        }

        # Filter constraints to verified rules
        filtered_constraints = [
            c for c in ctx.constraints
            if "must" in c.lower() or "mobile" in c.lower() or "wcag" in c.lower() or "api" in c.lower()
        ]

        # 4. Construct Original vs Optimized Context Objects
        original_context_dict = ctx.model_dump()

        optimized_context = {
            "project": ctx.intent.project_type,
            "goal": ctx.intent.primary_goal,
            "requirements": dense_reqs,
            "pages": optimized_pages,
            "components": optimized_components,
            "apis": optimized_apis,
            "data_schema": optimized_entities,
            "design": dense_design,
            "tech": dense_technical,
            "constraints": filtered_constraints,
        }

        pruning_summary = {
            "total_original_requirements": len(ctx.requirements),
            "preserved_requirements_count": len(preserved_requirements),
            "pruned_items": pruned_item_ids,
            "compressed_items": compressed_item_ids,
            "pruned_count": len(pruned_item_ids),
            "compressed_count": len(compressed_item_ids),
        }

        metrics = TokenCounter.compute_metrics(
            original_context=original_context_dict,
            optimized_context=optimized_context,
            all_requirements=ctx.requirements,
            preserved_requirements=preserved_requirements,
            pruning_summary=pruning_summary,
        )

        return optimized_context, metrics, preserved_requirements
