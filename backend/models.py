from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .context.evaluator import ContextScores
from .context.graph import DependencyGraphData
from .context.representation import (
    ContextSource,
    ContextStatus,
    IntentData,
    Requirement,
    RequirementCategory,
    RequirementPriority,
    StructuredContext,
    WebpageContext,
)
from .context.token_counter import OptimizationMetrics
from .state_machine import ProjectState


class Project(BaseModel):
    project_id: str
    project_name: Optional[str] = "Untitled Project"
    state: ProjectState = ProjectState.INITIAL
    original_prompt: str
    webpage_context: Optional[WebpageContext] = None
    context_representation: Optional[StructuredContext] = None
    graph: Optional[DependencyGraphData] = None
    evaluation_scores: Optional[Dict[str, ContextScores]] = None
    optimization_metrics: Optional[OptimizationMetrics] = None
    optimized_context: Optional[Dict[str, Any]] = None
    final_prompt: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# API Schemas
class CreateProjectRequest(BaseModel):
    original_prompt: str = Field(..., min_length=5, max_length=10000)
    project_name: Optional[str] = "Website Generation Project"
    context: Optional[WebpageContext] = None


class UpdateContextRequest(BaseModel):
    context: StructuredContext


class RetrieveContextRequest(BaseModel):
    item_id: Optional[str] = None
    entity_type: Optional[str] = None
    requirement_id: Optional[str] = None


class ContextApprovalRequest(BaseModel):
    approved: bool = True
    notes: Optional[str] = None


class PromptApprovalRequest(BaseModel):
    approved: bool = True
    edited_prompt: Optional[str] = None
