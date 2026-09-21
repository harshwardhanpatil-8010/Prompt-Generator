import json
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .representation import Requirement, RequirementPriority


class OptimizationMetrics(BaseModel):
    original_tokens: int = 0
    optimized_tokens: int = 0
    tokens_saved: int = 0
    token_reduction_percentage: float = 0.0
    total_requirements: int = 0
    preserved_requirements: int = 0
    requirement_coverage_percentage: float = 0.0
    critical_requirements_total: int = 0
    critical_requirements_preserved: int = 0
    critical_coverage_percentage: float = 0.0
    pruning_summary: Dict[str, Any] = Field(default_factory=dict)


class TokenCounter:
    """Calculates subword/word token counts and optimization metrics."""

    @staticmethod
    def count_tokens(text: str) -> int:
        if not text or not text.strip():
            return 0
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        return max(1, int(len(tokens) * 1.15))

    @classmethod
    def count_object_tokens(cls, obj: Any) -> int:
        if isinstance(obj, str):
            return cls.count_tokens(obj)
        serialized = json.dumps(obj, default=str, ensure_ascii=False, indent=2)
        return cls.count_tokens(serialized)

    @classmethod
    def compute_metrics(
        cls,
        original_context: Any,
        optimized_context: Any,
        all_requirements: List[Requirement],
        preserved_requirements: List[Requirement],
        pruning_summary: Optional[Dict[str, Any]] = None,
    ) -> OptimizationMetrics:
        orig_tokens = cls.count_object_tokens(original_context)
        opt_tokens = cls.count_object_tokens(optimized_context)

        tokens_saved = max(0, orig_tokens - opt_tokens)
        token_reduction_pct = (
            round((tokens_saved / orig_tokens) * 100, 2) if orig_tokens > 0 else 0.0
        )

        total_reqs = len(all_requirements)
        preserved_reqs = len(preserved_requirements)
        req_coverage_pct = (
            round((preserved_reqs / total_reqs) * 100, 2) if total_reqs > 0 else 100.0
        )

        critical_all = [
            r for r in all_requirements if r.priority == RequirementPriority.HIGH.value
        ]
        preserved_ids = {r.id for r in preserved_requirements}
        critical_preserved = [r for r in critical_all if r.id in preserved_ids]

        crit_total = len(critical_all)
        crit_pres = len(critical_preserved)
        crit_cov_pct = (
            round((crit_pres / crit_total) * 100, 2) if crit_total > 0 else 100.0
        )

        return OptimizationMetrics(
            original_tokens=orig_tokens,
            optimized_tokens=opt_tokens,
            tokens_saved=tokens_saved,
            token_reduction_percentage=token_reduction_pct,
            total_requirements=total_reqs,
            preserved_requirements=preserved_reqs,
            requirement_coverage_percentage=req_coverage_pct,
            critical_requirements_total=crit_total,
            critical_requirements_preserved=crit_pres,
            critical_coverage_percentage=crit_cov_pct,
            pruning_summary=pruning_summary or {},
        )
