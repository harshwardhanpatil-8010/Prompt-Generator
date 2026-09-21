from typing import Any, Dict, List, Optional
from .representation import StructuredContext
from .storage import ContextStore


class ContextRetriever:
    """Provides structured querying and dependency-aware retrieval over stored context."""

    def __init__(self, store: ContextStore):
        self.store = store

    def retrieve_by_project(self, project_id: str) -> Optional[StructuredContext]:
        return self.store.get_context(project_id)

    def retrieve_by_id(self, project_id: str, item_id: str) -> Optional[Any]:
        ctx = self.store.get_context(project_id)
        if not ctx:
            return None

        # Check all collections
        collections = [
            ctx.requirements,
            ctx.pages,
            ctx.components,
            ctx.apis,
            ctx.database_entities,
            ctx.tasks,
            ctx.assumptions,
            ctx.unknowns,
            ctx.decisions,
        ]

        for coll in collections:
            for item in coll:
                if getattr(item, "id", None) == item_id:
                    return item
        return None

    def retrieve_by_type(self, project_id: str, entity_type: str) -> List[Any]:
        return self.store.list_context_items(project_id, entity_type)

    def retrieve_by_requirement(self, project_id: str, req_id: str) -> Dict[str, List[Any]]:
        """Retrieve all pages, components, APIs, database entities, and tasks linked to a requirement."""
        ctx = self.store.get_context(project_id)
        if not ctx:
            return {}

        results: Dict[str, List[Any]] = {
            "requirement": [],
            "pages": [],
            "components": [],
            "apis": [],
            "database_entities": [],
            "tasks": [],
        }

        # Find requirement
        for r in ctx.requirements:
            if r.id == req_id:
                results["requirement"].append(r)

        # Related pages
        for p in ctx.pages:
            if req_id in p.requirements:
                results["pages"].append(p)

        # Related components
        for c in ctx.components:
            if req_id in c.requirements:
                results["components"].append(c)

        # Related APIs
        for a in ctx.apis:
            if req_id in a.requirements:
                results["apis"].append(a)

        # Related Entities
        for e in ctx.database_entities:
            if req_id in e.requirements:
                results["database_entities"].append(e)

        # Related Tasks
        for t in ctx.tasks:
            if req_id in t.requirements:
                results["tasks"].append(t)

        return results

    def retrieve_related_context(self, project_id: str, item_id: str) -> Dict[str, Any]:
        """Generic related context lookup based on ID prefix and links."""
        ctx = self.store.get_context(project_id)
        if not ctx:
            return {}

        item = self.retrieve_by_id(project_id, item_id)
        if not item:
            return {}

        if item_id.startswith("REQ-"):
            return self.retrieve_by_requirement(project_id, item_id)

        return {"item": item}
