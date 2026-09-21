from backend.context.representation import Requirement, StructuredContext
from backend.context.storage import InMemoryContextStore
from backend.models import Project


def test_in_memory_context_store():
    store = InMemoryContextStore()

    # Save Project
    project = Project(
        project_id="proj-1",
        original_prompt="Build a fitness gym website",
    )
    store.save_project(project)
    assert store.get_project("proj-1") is not None

    # Save Context
    ctx = StructuredContext(
        requirements=[
            Requirement(
                id="REQ-001",
                title="Hero Section",
                description="Prominent hero banner",
            )
        ]
    )
    store.save_context("proj-1", ctx)

    retrieved = store.get_context("proj-1")
    assert retrieved is not None
    assert len(retrieved.requirements) == 1
    assert retrieved.requirements[0].id == "REQ-001"

    # List items
    items = store.list_context_items("proj-1", "requirements")
    assert len(items) == 1

    # Delete
    deleted = store.delete_context("proj-1")
    assert deleted is True
    assert store.get_context("proj-1") is None
