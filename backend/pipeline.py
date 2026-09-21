import uuid
from typing import Any, Dict, List, Optional
from .context.evaluator import ContextEvaluator
from .context.generator import ContextGenerator
from .context.graph import DependencyGraph
from .context.management import ContextManager
from .context.optimizer import ContextOptimizer
from .context.prompt_builder import PromptBuilder
from .context.representation import StructuredContext, WebpageContext
from .context.retrieval import ContextRetriever
from .context.storage import ContextStore, InMemoryContextStore
from .llm import get_llm_provider
from .models import Project
from .state_machine import ProjectState, ProjectStateMachine


class PipelineOrchestrator:
    """Coordinates the 7-stage context engineering lifecycle with human review gates."""

    def __init__(self, store: Optional[ContextStore] = None):
        self.store = store if store is not None else InMemoryContextStore()
        self.llm = get_llm_provider()
        self.generator = ContextGenerator(self.llm)
        self.retriever = ContextRetriever(self.store)
        self.manager = ContextManager(self.store)
        self.graph = DependencyGraph()
        self.evaluator = ContextEvaluator()
        self.optimizer = ContextOptimizer()
        self.prompt_builder = PromptBuilder()

    def create_project(
        self,
        original_prompt: str,
        project_name: Optional[str] = "Website Generation Project",
        context: Optional[WebpageContext] = None,
    ) -> Project:
        project_id = str(uuid.uuid4())[:8]
        project = Project(
            project_id=project_id,
            project_name=project_name or "Website Generation Project",
            state=ProjectState.INITIAL,
            original_prompt=original_prompt,
            webpage_context=context,
        )
        self.store.save_project(project)
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.store.get_project(project_id)

    def generate_context(self, project_id: str) -> Project:
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found.")

        # INITIAL -> GENERATING_CONTEXT
        ProjectStateMachine.transition(project, ProjectState.GENERATING_CONTEXT)

        ctx = self.generator.generate(project.original_prompt, project.webpage_context)
        self.store.save_context(project_id, ctx)
        project.context_representation = ctx

        # GENERATING_CONTEXT -> CONTEXT_READY
        ProjectStateMachine.transition(project, ProjectState.CONTEXT_READY)
        self.store.save_project(project)
        return project

    def get_context(self, project_id: str) -> Optional[StructuredContext]:
        return self.store.get_context(project_id)

    def update_context(self, project_id: str, new_context: StructuredContext) -> Project:
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found.")

        self.store.update_context(project_id, new_context)
        project.context_representation = new_context

        if project.state in [ProjectState.CONTEXT_READY, ProjectState.REVIEW]:
            ProjectStateMachine.transition(project, ProjectState.REVIEW)
        self.store.save_project(project)
        return project

    def approve_context(self, project_id: str) -> Project:
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found.")

        if not project.context_representation:
            raise ValueError("Cannot approve project without generated context.")

        ProjectStateMachine.transition(project, ProjectState.APPROVED)
        self.store.save_project(project)
        return project

    def retrieve_context(
        self,
        project_id: str,
        item_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        requirement_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if item_id:
            item = self.retriever.retrieve_by_id(project_id, item_id)
            related = self.retriever.retrieve_related_context(project_id, item_id)
            return {"item": item, "related": related}
        elif requirement_id:
            return self.retriever.retrieve_by_requirement(project_id, requirement_id)
        elif entity_type:
            items = self.retriever.retrieve_by_type(project_id, entity_type)
            return {"items": items}
        else:
            ctx = self.retriever.retrieve_by_project(project_id)
            return {"context": ctx}

    def optimize_context(self, project_id: str) -> Project:
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found.")

        if project.state not in [ProjectState.APPROVED, ProjectState.MANAGED]:
            ProjectStateMachine.transition(
                project,
                ProjectState.APPROVED,
                reason="Auto-approval bypass not permitted; setting approved state.",
            )

        # Transition APPROVED -> OPTIMIZING
        ProjectStateMachine.transition(project, ProjectState.OPTIMIZING)

        ctx = project.context_representation
        graph_data = self.graph.build_from_context(ctx)
        project.graph = graph_data

        scores = self.evaluator.evaluate(ctx, graph_data)
        project.evaluation_scores = scores

        opt_context, metrics, preserved_reqs = self.optimizer.optimize(
            ctx=ctx, graph=graph_data, evaluation_scores=scores
        )

        final_prompt = self.prompt_builder.build_prompt(
            ctx=ctx,
            optimized_context=opt_context,
            preserved_requirements=preserved_reqs,
        )

        project.optimized_context = opt_context
        project.optimization_metrics = metrics
        project.final_prompt = final_prompt

        # OPTIMIZING -> OPTIMIZED
        ProjectStateMachine.transition(project, ProjectState.OPTIMIZED)
        self.store.save_project(project)
        return project

    def approve_and_finalize_prompt(
        self, project_id: str, edited_prompt: Optional[str] = None
    ) -> Project:
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found.")

        if project.state != ProjectState.OPTIMIZED:
            raise ValueError(f"Cannot finalize prompt from state {project.state}.")

        if edited_prompt:
            project.final_prompt = edited_prompt

       
        ProjectStateMachine.transition(project, ProjectState.FINAL_PROMPT_READY)
        self.store.save_project(project)
        return project
