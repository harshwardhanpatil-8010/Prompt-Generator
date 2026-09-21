from typing import Any, Dict, List, Optional
from .representation import (
    APISpec,
    AssumptionItem,
    ComponentSpec,
    ContextSource,
    ContextStatus,
    DatabaseEntity,
    DecisionItem,
    PageSpec,
    Requirement,
    StructuredContext,
    TaskSpec,
    UnknownItem,
)
from .storage import ContextStore


class ContextManager:
    """Manages context lifecycle, updates, status transitions, and relational consistency."""

    def __init__(self, store: ContextStore):
        self.store = store

    def update_item_status(
        self, project_id: str, item_id: str, new_status: ContextStatus
    ) -> bool:
        ctx = self.store.get_context(project_id)
        if not ctx:
            return False

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
                    item.status = new_status.value
                    self.store.update_context(project_id, ctx)
                    return True
        return False

    def update_item_source(
        self, project_id: str, item_id: str, new_source: ContextSource
    ) -> bool:
        ctx = self.store.get_context(project_id)
        if not ctx:
            return False

        collections = [
            ctx.requirements,
            ctx.pages,
            ctx.components,
            ctx.apis,
            ctx.database_entities,
            ctx.tasks,
            ctx.assumptions,
            ctx.unknowns,
        ]

        for coll in collections:
            for item in coll:
                if getattr(item, "id", None) == item_id:
                    item.source = new_source.value
                    self.store.update_context(project_id, ctx)
                    return True
        return False

    def add_requirement(self, project_id: str, req: Requirement) -> StructuredContext:
        ctx = self.store.get_context(project_id)
        if not ctx:
            raise ValueError(f"Context for project {project_id} not found.")

        # Check existing
        existing_ids = {r.id for r in ctx.requirements}
        if req.id in existing_ids:
            # Update existing
            ctx.requirements = [r if r.id != req.id else req for r in ctx.requirements]
        else:
            ctx.requirements.append(req)

        return self.store.update_context(project_id, ctx)

    def remove_item(self, project_id: str, item_id: str) -> bool:
        ctx = self.store.get_context(project_id)
        if not ctx:
            return False

        changed = False
        if item_id.startswith("REQ-"):
            prev_len = len(ctx.requirements)
            ctx.requirements = [r for r in ctx.requirements if r.id != item_id]
            changed = len(ctx.requirements) != prev_len
        elif item_id.startswith("PAGE-"):
            prev_len = len(ctx.pages)
            ctx.pages = [p for p in ctx.pages if p.id != item_id]
            changed = len(ctx.pages) != prev_len
        elif item_id.startswith("COMP-"):
            prev_len = len(ctx.components)
            ctx.components = [c for c in ctx.components if c.id != item_id]
            changed = len(ctx.components) != prev_len
        elif item_id.startswith("API-"):
            prev_len = len(ctx.apis)
            ctx.apis = [a for a in ctx.apis if a.id != item_id]
            changed = len(ctx.apis) != prev_len
        elif item_id.startswith("DB-"):
            prev_len = len(ctx.database_entities)
            ctx.database_entities = [e for e in ctx.database_entities if e.id != item_id]
            changed = len(ctx.database_entities) != prev_len
        elif item_id.startswith("TASK-"):
            prev_len = len(ctx.tasks)
            ctx.tasks = [t for t in ctx.tasks if t.id != item_id]
            changed = len(ctx.tasks) != prev_len
        elif item_id.startswith("ASSUMP-"):
            prev_len = len(ctx.assumptions)
            ctx.assumptions = [a for a in ctx.assumptions if a.id != item_id]
            changed = len(ctx.assumptions) != prev_len
        elif item_id.startswith("UNK-"):
            prev_len = len(ctx.unknowns)
            ctx.unknowns = [u for u in ctx.unknowns if u.id != item_id]
            changed = len(ctx.unknowns) != prev_len

        if changed:
            self.store.update_context(project_id, ctx)
        return changed

    def merge_context(self, project_id: str, incoming_ctx: StructuredContext) -> StructuredContext:
        ctx = self.store.get_context(project_id)
        if not ctx:
            return self.store.save_context(project_id, incoming_ctx)

        # Merge requirements
        req_map = {r.id: r for r in ctx.requirements}
        for r in incoming_ctx.requirements:
            req_map[r.id] = r
        ctx.requirements = list(req_map.values())

        # Merge pages
        page_map = {p.id: p for p in ctx.pages}
        for p in incoming_ctx.pages:
            page_map[p.id] = p
        ctx.pages = list(page_map.values())

        # Merge components
        comp_map = {c.id: c for c in ctx.components}
        for c in incoming_ctx.components:
            comp_map[c.id] = c
        ctx.components = list(comp_map.values())

        # Merge APIs
        api_map = {a.id: a for a in ctx.apis}
        for a in incoming_ctx.apis:
            api_map[a.id] = a
        ctx.apis = list(api_map.values())

        # Merge entities
        db_map = {e.id: e for e in ctx.database_entities}
        for e in incoming_ctx.database_entities:
            db_map[e.id] = e
        ctx.database_entities = list(db_map.values())

        # Merge tasks
        task_map = {t.id: t for t in ctx.tasks}
        for t in incoming_ctx.tasks:
            task_map[t.id] = t
        ctx.tasks = list(task_map.values())

        # Update design & tech if provided
        if incoming_ctx.design:
            ctx.design = incoming_ctx.design
        if incoming_ctx.technical:
            ctx.technical = incoming_ctx.technical

        return self.store.update_context(project_id, ctx)
