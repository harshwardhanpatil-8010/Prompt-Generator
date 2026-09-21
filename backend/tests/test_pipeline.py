from backend.context.representation import WebpageContext
from backend.pipeline import PipelineOrchestrator


def test_pipeline_end_to_end_context_lifecycle():
    orchestrator = PipelineOrchestrator()
    prompt = "Create a modern e-commerce website for a sneaker store with catalog, size selector, and cart."
    context = WebpageContext(
        page_title="Hype Kicks Store",
        page_url="https://hypekicks.example.com",
        selected_text="Exclusive sneaker drops, streetwear apparel, free worldwide shipping.",
        enabled=True,
    )

    # 1. Create Project (INITIAL)
    project = orchestrator.create_project(
        original_prompt=prompt, project_name="Sneaker Drop Site", context=context
    )
    assert project.project_id is not None
    assert project.state == "INITIAL"

    # 2. Generate Context (GENERATING_CONTEXT -> CONTEXT_READY)
    orchestrator.generate_context(project.project_id)
    assert project.context_representation is not None
    assert project.state == "CONTEXT_READY"

    # 3. Approve Context (CONTEXT_READY -> APPROVED)
    orchestrator.approve_context(project.project_id)
    assert project.state == "APPROVED"

    # 4. Optimize Context (APPROVED -> OPTIMIZING -> OPTIMIZED)
    orchestrator.optimize_context(project.project_id)
    assert project.state == "OPTIMIZED"
    assert project.optimization_metrics is not None
    assert project.final_prompt is not None
    assert "=== AI WEBSITE GENERATION SPECIFICATION ===" in project.final_prompt
    assert "CORE REQUIREMENTS:" in project.final_prompt

    # 5. Finalize Prompt (OPTIMIZED -> FINAL_PROMPT_READY)
    orchestrator.approve_and_finalize_prompt(project.project_id)
    assert project.state == "FINAL_PROMPT_READY"
