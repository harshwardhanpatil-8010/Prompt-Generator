from backend.context.evaluator import ContextEvaluator
from backend.context.graph import DependencyGraph
from backend.context.optimizer import ContextOptimizer
from backend.llm.mock import MockLLMProvider


def test_context_optimizer_token_reduction_and_coverage():
    provider = MockLLMProvider()
    prompt = "Create a modern e-commerce website for a sneaker store with catalog and cart."
    intent = provider.extract_intent(prompt)
    reqs = provider.expand_requirements(intent, prompt)
    ctx = provider.generate_specification(intent, reqs, prompt)

    graph_engine = DependencyGraph()
    graph_data = graph_engine.build_from_context(ctx)

    evaluator = ContextEvaluator()
    scores = evaluator.evaluate(ctx, graph_data)

    optimizer = ContextOptimizer()
    optimized_context, metrics, preserved_reqs = optimizer.optimize(
        ctx=ctx, graph=graph_data, evaluation_scores=scores
    )

    # Verify token reduction is substantial (approx 50% or greater)
    assert metrics.token_reduction_percentage >= 45.0
    assert metrics.tokens_saved > 0
    assert metrics.optimized_tokens < metrics.original_tokens

    # Verify 100% critical requirement coverage
    assert metrics.critical_coverage_percentage == 100.0
    assert metrics.critical_requirements_preserved == metrics.critical_requirements_total

    # Verify preserved requirements contain core user features
    preserved_ids = {r.id for r in preserved_reqs}
    assert "REQ-001" in preserved_ids
    assert "REQ-002" in preserved_ids
    assert "REQ-008" in preserved_ids
    assert "REQ-009" in preserved_ids
