from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .representation import StructuredContext


class ContextStore(ABC):
    """Abstract interface for context persistence."""

    @abstractmethod
    def save_project(self, project_data: Any) -> Any:
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def save_context(self, project_id: str, context: StructuredContext) -> StructuredContext:
        pass

    @abstractmethod
    def get_context(self, project_id: str) -> Optional[StructuredContext]:
        pass

    @abstractmethod
    def update_context(self, project_id: str, context: StructuredContext) -> StructuredContext:
        pass

    @abstractmethod
    def delete_context(self, project_id: str) -> bool:
        pass

    @abstractmethod
    def list_context_items(self, project_id: str, entity_type: Optional[str] = None) -> List[Any]:
        pass


class InMemoryContextStore(ContextStore):
    """Thread-safe in-memory store for projects and structured contexts."""

    def __init__(self):
        self._projects: Dict[str, Any] = {}
        self._contexts: Dict[str, StructuredContext] = {}

    def save_project(self, project: Any) -> Any:
        self._projects[project.project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[Any]:
        return self._projects.get(project_id)

    def list_projects(self) -> List[Any]:
        return list(self._projects.values())

    def save_context(self, project_id: str, context: StructuredContext) -> StructuredContext:
        self._contexts[project_id] = context
        if project_id in self._projects:
            self._projects[project_id].context_representation = context
        return context

    def get_context(self, project_id: str) -> Optional[StructuredContext]:
        return self._contexts.get(project_id)

    def update_context(self, project_id: str, context: StructuredContext) -> StructuredContext:
        self._contexts[project_id] = context
        if project_id in self._projects:
            self._projects[project_id].context_representation = context
        return context

    def delete_context(self, project_id: str) -> bool:
        if project_id in self._contexts:
            del self._contexts[project_id]
            if project_id in self._projects:
                self._projects[project_id].context_representation = None
            return True
        return False

    def list_context_items(self, project_id: str, entity_type: Optional[str] = None) -> List[Any]:
        ctx = self.get_context(project_id)
        if not ctx:
            return []

        mapping = {
            "requirements": ctx.requirements,
            "pages": ctx.pages,
            "components": ctx.components,
            "apis": ctx.apis,
            "database_entities": ctx.database_entities,
            "tasks": ctx.tasks,
            "assumptions": ctx.assumptions,
            "unknowns": ctx.unknowns,
            "decisions": ctx.decisions,
        }

        if entity_type:
            return mapping.get(entity_type.lower(), [])

        # Return flattened list of all identifiable items
        items = []
        for group in mapping.values():
            items.extend(group)
        return items
