from backend.context.representation import (
    APISpec,
    ComponentSpec,
    PageSpec,
    Requirement,
    StructuredContext,
)
from backend.context.retrieval import ContextRetriever
from backend.context.storage import InMemoryContextStore


def test_context_retriever():
    store = InMemoryContextStore()
    retriever = ContextRetriever(store)

    ctx = StructuredContext(
        requirements=[
            Requirement(
                id="REQ-001",
                title="Hero Banner",
                description="Hero banner for the website",
            ),
            Requirement(
                id="REQ-002",
                title="Product Catalog",
                description="Interactive product catalog",
            ),
        ],
        pages=[
            PageSpec(
                id="PAGE-001",
                name="Home",
                path="/",
                purpose="Landing page",
                requirements=["REQ-001", "REQ-002"],
            )
        ],
        components=[
            ComponentSpec(
                id="COMP-001",
                name="HeroComponent",
                type="layout",
                description="Hero component",
                requirements=["REQ-001"],
            )
        ],
        apis=[
            APISpec(
                id="API-001",
                endpoint="/api/products",
                method="GET",
                description="Get products",
                requirements=["REQ-002"],
            )
        ],
    )
    store.save_context("proj-100", ctx)

    # 1. Retrieve by ID
    item = retriever.retrieve_by_id("proj-100", "REQ-001")
    assert item is not None
    assert item.title == "Hero Banner"

    # 2. Retrieve by entity type
    reqs = retriever.retrieve_by_type("proj-100", "requirements")
    assert len(reqs) == 2

    # 3. Retrieve by requirement relations
    rel_req1 = retriever.retrieve_by_requirement("proj-100", "REQ-001")
    assert len(rel_req1["pages"]) == 1
    assert len(rel_req1["components"]) == 1

    rel_req2 = retriever.retrieve_by_requirement("proj-100", "REQ-002")
    assert len(rel_req2["apis"]) == 1
