from backend.context.management import ContextManager
from backend.context.representation import (
    ContextSource,
    ContextStatus,
    Requirement,
    StructuredContext,
)
from backend.context.storage import InMemoryContextStore


def test_context_manager_crud_and_status():
    store = InMemoryContextStore()
    manager = ContextManager(store)

    ctx = StructuredContext(
        requirements=[
            Requirement(
                id="REQ-001",
                title="Hero Banner",
                description="Initial description",
                status=ContextStatus.ACTIVE.value,
            )
        ]
    )
    store.save_context("proj-200", ctx)

    # 1. Update status
    success = manager.update_item_status("proj-200", "REQ-001", ContextStatus.APPROVED)
    assert success is True
    updated_ctx = store.get_context("proj-200")
    assert updated_ctx.requirements[0].status == ContextStatus.APPROVED.value

    # 2. Update source
    success_src = manager.update_item_source("proj-200", "REQ-001", ContextSource.USER)
    assert success_src is True
    assert store.get_context("proj-200").requirements[0].source == ContextSource.USER.value

    # 3. Add requirement
    new_req = Requirement(
        id="REQ-002",
        title="Checkout Flow",
        description="Cart and checkout",
    )
    manager.add_requirement("proj-200", new_req)
    assert len(store.get_context("proj-200").requirements) == 2

    # 4. Remove requirement
    manager.remove_item("proj-200", "REQ-002")
    assert len(store.get_context("proj-200").requirements) == 1
