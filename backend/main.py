import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .context.representation import StructuredContext
from .context.storage import InMemoryContextStore
from .models import (
    ContextApprovalRequest,
    CreateProjectRequest,
    Project,
    PromptApprovalRequest,
    RetrieveContextRequest,
    UpdateContextRequest,
)
from .pipeline import PipelineOrchestrator
from .state_machine import InvalidStateTransitionError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompt_generator")

app = FastAPI(
    title="AI Context-Engineered Website Generation System API",
    description="Transforms high-level website requirements into structured, stored, retrievable, and optimized context representations with a minimum-sufficient prompt.",
    version="1.0.0",
)

# CORS configuration for Chrome Extension and local clients
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*|http://localhost:.*|http://127\.0\.0\.1:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe in-memory store and pipeline orchestrator
context_store = InMemoryContextStore()
orchestrator = PipelineOrchestrator(context_store)


import os
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

# Mount frontend web application if present
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/", tags=["System"])
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and "application/json" not in accept:
        return RedirectResponse(url="/app/")
    return {
        "name": "AI Context-Engineered Website Generation System",
        "version": "1.0.0",
        "status": "online",
        "provider": settings.LLM_PROVIDER,
        "app_ui": "/app",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "projects_count": len(context_store.list_projects()),
    }


@app.post(
    "/projects",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
)
def create_project(req: CreateProjectRequest):
    if len(req.original_prompt.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Requirement prompt must be at least 5 characters long.",
        )
    if len(req.original_prompt) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement prompt exceeds maximum length limit (10,000 characters).",
        )

    project = orchestrator.create_project(
        original_prompt=req.original_prompt.strip(),
        project_name=req.project_name,
        context=req.context,
    )
    return project


@app.get("/projects/{project_id}", response_model=Project, tags=["Projects"])
def get_project(project_id: str):
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return project


@app.post(
    "/projects/{project_id}/context/generate",
    response_model=Project,
    tags=["Context Lifecycle"],
)
def generate_context(project_id: str):
    try:
        return orchestrator.generate_context(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Context generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get(
    "/projects/{project_id}/context",
    response_model=StructuredContext,
    tags=["Context Lifecycle"],
)
def get_context(project_id: str):
    ctx = orchestrator.get_context(project_id)
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context for project '{project_id}' has not been generated yet.",
        )
    return ctx


@app.put(
    "/projects/{project_id}/context",
    response_model=Project,
    tags=["Context Lifecycle"],
)
def update_context(project_id: str, req: UpdateContextRequest):
    try:
        return orchestrator.update_context(project_id, req.context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/projects/{project_id}/context/approve",
    response_model=Project,
    tags=["Context Lifecycle"],
)
def approve_context(project_id: str, req: Optional[ContextApprovalRequest] = None):
    try:
        return orchestrator.approve_context(project_id)
    except (ValueError, InvalidStateTransitionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/projects/{project_id}/context/retrieve",
    tags=["Context Retrieval"],
)
def retrieve_context(project_id: str, req: RetrieveContextRequest):
    try:
        return orchestrator.retrieve_context(
            project_id=project_id,
            item_id=req.item_id,
            entity_type=req.entity_type,
            requirement_id=req.requirement_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/projects/{project_id}/context/optimize",
    response_model=Project,
    tags=["Context Optimization"],
)
def optimize_context(project_id: str):
    try:
        return orchestrator.optimize_context(project_id)
    except (ValueError, InvalidStateTransitionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Context optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get(
    "/projects/{project_id}/optimization",
    tags=["Context Optimization"],
)
def get_optimization_results(project_id: str):
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    if not project.optimization_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has not been optimized yet.",
        )
    return {
        "project_id": project.project_id,
        "state": project.state,
        "metrics": project.optimization_metrics,
        "optimized_context": project.optimized_context,
        "final_prompt": project.final_prompt,
    }


@app.post(
    "/projects/{project_id}/prompt",
    tags=["Final Prompt"],
)
def get_or_build_prompt(project_id: str):
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    if not project.final_prompt:
        # Run optimization if needed
        project = orchestrator.optimize_context(project_id)
    return {
        "project_id": project.project_id,
        "state": project.state,
        "final_prompt": project.final_prompt,
    }


@app.post(
    "/projects/{project_id}/prompt/approve",
    response_model=Project,
    tags=["Final Prompt"],
)
def approve_prompt(project_id: str, req: Optional[PromptApprovalRequest] = None):
    try:
        edited_prompt = req.edited_prompt if req else None
        return orchestrator.approve_and_finalize_prompt(project_id, edited_prompt)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
