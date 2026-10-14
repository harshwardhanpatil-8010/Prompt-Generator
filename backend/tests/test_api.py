from fastapi.testclient import TestClient
from backend.main import app, context_store

client = TestClient(app)


def setup_function():
    # Clear in-memory store before each test
    context_store._projects.clear()
    context_store._contexts.clear()


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Context-Engineered Website Generation System"
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["llm_provider"] in ["mock", "ollama"]


def test_create_project_validation():
    # Too short (< 5 chars triggers 422)
    res_short = client.post("/projects", json={"original_prompt": "abc"})
    assert res_short.status_code == 422

    # Valid
    res_valid = client.post(
        "/projects",
        json={
            "original_prompt": "Create a modern e-commerce website for a sneaker store.",
            "project_name": "Sneaker Store",
        },
    )
    assert res_valid.status_code == 201
    data = res_valid.json()
    assert "project_id" in data
    assert data["state"] == "INITIAL"


def test_invalid_project_id():
    res = client.get("/projects/non_existent_id")
    assert res.status_code == 404


def test_full_context_lifecycle_api():
    # 1. Create Project
    create_res = client.post(
        "/projects",
        json={
            "original_prompt": "Create a modern e-commerce website for a sneaker store with catalog, size selector, and cart.",
            "project_name": "Sneaker Hub",
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["project_id"]

    # 2. Generate Context
    gen_res = client.post(f"/projects/{project_id}/context/generate")
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["state"] == "CONTEXT_READY"
    assert gen_data["context_representation"] is not None

    # 3. Retrieve Context
    get_ctx_res = client.get(f"/projects/{project_id}/context")
    assert get_ctx_res.status_code == 200
    ctx_data = get_ctx_res.json()
    assert len(ctx_data["requirements"]) > 0
    assert len(ctx_data["pages"]) > 0

    # 4. Context Query Retrieval
    ret_res = client.post(
        f"/projects/{project_id}/context/retrieve",
        json={"item_id": "REQ-001"},
    )
    assert ret_res.status_code == 200
    assert ret_res.json()["item"]["id"] == "REQ-001"

    # 5. Update Context (Human review edit)
    ctx_data["design"]["visual_style"] = "Retro Neon Streetwear"
    put_ctx_res = client.put(
        f"/projects/{project_id}/context",
        json={"context": ctx_data},
    )
    assert put_ctx_res.status_code == 200
    assert put_ctx_res.json()["context_representation"]["design"]["visual_style"] == "Retro Neon Streetwear"

    # 6. Approve Context Gate
    approve_res = client.post(f"/projects/{project_id}/context/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["state"] == "APPROVED"

    # 7. Optimize Context
    opt_res = client.post(f"/projects/{project_id}/context/optimize")
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    metrics = opt_data["optimization_metrics"]
    assert metrics["token_reduction_percentage"] >= 45.0
    assert metrics["critical_coverage_percentage"] == 100.0
    assert "=== AI WEBSITE GENERATION SPECIFICATION ===" in opt_data["final_prompt"]

    # 8. Get Optimization
    get_opt_res = client.get(f"/projects/{project_id}/optimization")
    assert get_opt_res.status_code == 200

    # 9. Prompt Endpoint
    prompt_res = client.post(f"/projects/{project_id}/prompt")
    assert prompt_res.status_code == 200
    assert "final_prompt" in prompt_res.json()

    # 10. Approve Final Prompt Gate
    prompt_app_res = client.post(
        f"/projects/{project_id}/prompt/approve",
        json={"approved": True},
    )
    assert prompt_app_res.status_code == 200
    assert prompt_app_res.json()["state"] == "FINAL_PROMPT_READY"

    # 11. Idempotent re-entry when navigating back in UI
    re_approve = client.post(f"/projects/{project_id}/context/approve")
    assert re_approve.status_code == 200
    re_optimize = client.post(f"/projects/{project_id}/context/optimize")
    assert re_optimize.status_code == 200
