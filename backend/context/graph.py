from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from .representation import RequirementPriority, StructuredContext


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # requirement, page, component, api, entity, task
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str


class DependencyGraphData(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    critical_path_node_ids: List[str] = Field(default_factory=list)
    isolated_node_ids: List[str] = Field(default_factory=list)


class DependencyGraph:
    """In-memory dependency graph modeling requirements and architecture entities."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adj_out: Dict[str, Set[str]] = defaultdict(set)
        self._adj_in: Dict[str, Set[str]] = defaultdict(set)
        self._adj_all: Dict[str, Set[str]] = defaultdict(set)

    def add_node(self, id: str, label: str, type: str, metadata: Optional[Dict[str, Any]] = None):
        node = GraphNode(id=id, label=label, type=type, metadata=metadata or {})
        self.nodes[id] = node

    def remove_node(self, id: str):
        if id in self.nodes:
            del self.nodes[id]
            self.edges = [e for e in self.edges if e.source != id and e.target != id]
            self._rebuild_adjacency()

    def add_edge(self, source: str, target: str, relation_type: str):
        edge = GraphEdge(source=source, target=target, relation_type=relation_type)
        self.edges.append(edge)
        self._adj_out[source].add(target)
        self._adj_in[target].add(source)
        self._adj_all[source].add(target)
        self._adj_all[target].add(source)

    def remove_edge(self, source: str, target: str):
        self.edges = [e for e in self.edges if not (e.source == source and e.target == target)]
        self._rebuild_adjacency()

    def _rebuild_adjacency(self):
        self._adj_out.clear()
        self._adj_in.clear()
        self._adj_all.clear()
        for e in self.edges:
            self._adj_out[e.source].add(e.target)
            self._adj_in[e.target].add(e.source)
            self._adj_all[e.source].add(e.target)
            self._adj_all[e.target].add(e.source)

    def get_dependencies(self, node_id: str) -> List[str]:
        """Get downstream nodes that node_id depends on."""
        return list(self._adj_out.get(node_id, set()))

    def get_dependents(self, node_id: str) -> List[str]:
        """Get upstream nodes that depend on node_id."""
        return list(self._adj_in.get(node_id, set()))

    def get_related_context(self, node_id: str, max_depth: int = 3) -> Set[str]:
        """BFS to collect all transitive related nodes within max_depth."""
        visited: Set[str] = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            curr, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for neighbor in self._adj_all.get(curr, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        return visited

    def build_from_context(self, ctx: StructuredContext) -> DependencyGraphData:
        self.nodes.clear()
        self.edges.clear()

        # 1. Requirements
        for req in ctx.requirements:
            self.add_node(
                id=req.id,
                label=f"{req.id}: {req.title}",
                type="requirement",
                metadata={"priority": req.priority, "category": req.category, "source": req.source},
            )
            for dep in req.dependencies:
                self.add_edge(req.id, dep, "depends_on_requirement")

        # 2. Pages
        for p in ctx.pages:
            self.add_node(
                id=p.id,
                label=f"{p.id}: {p.name}",
                type="page",
                metadata={"path": p.path},
            )
            for req_id in p.requirements:
                if req_id in self.nodes:
                    self.add_edge(req_id, p.id, "implements_on_page")
            for comp_id in p.components:
                self.add_edge(p.id, comp_id, "contains_component")

        # 3. Components
        for c in ctx.components:
            self.add_node(
                id=c.id,
                label=f"{c.id}: {c.name}",
                type="component",
                metadata={"type": c.type},
            )
            for req_id in c.requirements:
                if req_id in self.nodes:
                    self.add_edge(req_id, c.id, "specifies_component")

        # 4. APIs
        for a in ctx.apis:
            self.add_node(
                id=a.id,
                label=f"{a.id}: {a.method} {a.endpoint}",
                type="api",
                metadata={"method": a.method, "endpoint": a.endpoint},
            )
            for req_id in a.requirements:
                if req_id in self.nodes:
                    self.add_edge(req_id, a.id, "specifies_api")

        # 5. Database Entities
        for e in ctx.database_entities:
            self.add_node(
                id=e.id,
                label=f"{e.id}: {e.name}",
                type="entity",
                metadata={"fields_count": len(e.fields)},
            )
            for req_id in e.requirements:
                if req_id in self.nodes:
                    self.add_edge(req_id, e.id, "specifies_database_entity")

        # 6. Tasks
        for t in ctx.tasks:
            self.add_node(
                id=t.id,
                label=f"{t.id}: {t.title}",
                type="task",
                metadata={"priority": t.priority},
            )
            for req_id in t.requirements:
                if req_id in self.nodes:
                    self.add_edge(t.id, req_id, "implements_requirement")

        self._rebuild_adjacency()

        # Identify isolated nodes
        isolated_nodes = [
            node.id for node in self.nodes.values() if len(self._adj_all[node.id]) == 0
        ]

        # Identify critical path nodes
        critical_nodes: Set[str] = set()
        for req in ctx.requirements:
            if req.priority == RequirementPriority.HIGH.value:
                critical_nodes.add(req.id)
                critical_nodes.update(self.get_related_context(req.id, max_depth=4))

        return DependencyGraphData(
            nodes=list(self.nodes.values()),
            edges=self.edges,
            critical_path_node_ids=list(critical_nodes),
            isolated_node_ids=isolated_nodes,
        )
