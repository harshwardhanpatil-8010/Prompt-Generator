from backend.context.graph import DependencyGraph
from backend.llm.mock import MockLLMProvider


def test_dependency_graph_building_and_traversal():
    provider = MockLLMProvider()
    prompt = "Create a modern e-commerce website for a sneaker store with catalog and cart."
    intent = provider.extract_intent(prompt)
    reqs = provider.expand_requirements(intent, prompt)
    ctx = provider.generate_specification(intent, reqs, prompt)

    graph = DependencyGraph()
    graph_data = graph.build_from_context(ctx)

    assert len(graph_data.nodes) > 0
    assert len(graph_data.edges) > 0

    node_types = {n.type for n in graph_data.nodes}
    assert "requirement" in node_types
    assert "page" in node_types
    assert "component" in node_types
    assert "api" in node_types
    assert "entity" in node_types
    assert "task" in node_types

    # Node operations
    graph.add_node("TEST-01", "Test Node", "custom")
    assert "TEST-01" in graph.nodes
    graph.remove_node("TEST-01")
    assert "TEST-01" not in graph.nodes

    # Traversal check
    related = graph.get_related_context("REQ-001")
    assert len(related) > 0
