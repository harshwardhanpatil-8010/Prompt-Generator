from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Set


class ProjectState(str, Enum):
    INITIAL = "INITIAL"
    GENERATING_CONTEXT = "GENERATING_CONTEXT"
    CONTEXT_READY = "CONTEXT_READY"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    MANAGED = "MANAGED"
    OPTIMIZING = "OPTIMIZING"
    OPTIMIZED = "OPTIMIZED"
    FINAL_PROMPT_READY = "FINAL_PROMPT_READY"
    ERROR = "ERROR"


class InvalidStateTransitionError(Exception):
    def __init__(self, current_state: ProjectState, target_state: ProjectState, reason: str = ""):
        message = f"Invalid state transition from {current_state.value} to {target_state.value}."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)
        self.current_state = current_state
        self.target_state = target_state
        self.reason = reason


class ProjectStateMachine:
    """Enforces valid state lifecycle transitions and human-in-the-loop approval gates."""

    VALID_TRANSITIONS: Dict[ProjectState, Set[ProjectState]] = {
        ProjectState.INITIAL: {
            ProjectState.GENERATING_CONTEXT,
            ProjectState.ERROR,
        },
        ProjectState.GENERATING_CONTEXT: {
            ProjectState.CONTEXT_READY,
            ProjectState.ERROR,
        },
        ProjectState.CONTEXT_READY: {
            ProjectState.REVIEW,
            ProjectState.APPROVED,
            ProjectState.ERROR,
        },
        ProjectState.REVIEW: {
            ProjectState.CONTEXT_READY,
            ProjectState.APPROVED,
            ProjectState.MANAGED,
            ProjectState.ERROR,
        },
        ProjectState.APPROVED: {
            ProjectState.MANAGED,
            ProjectState.OPTIMIZING,
            ProjectState.ERROR,
        },
        ProjectState.MANAGED: {
            ProjectState.OPTIMIZING,
            ProjectState.APPROVED,
            ProjectState.REVIEW,
            ProjectState.ERROR,
        },
        ProjectState.OPTIMIZING: {
            ProjectState.OPTIMIZED,
            ProjectState.ERROR,
        },
        ProjectState.OPTIMIZED: {
            ProjectState.FINAL_PROMPT_READY,
            ProjectState.REVIEW,
            ProjectState.MANAGED,
            ProjectState.ERROR,
        },
        ProjectState.FINAL_PROMPT_READY: {
            ProjectState.INITIAL,
            ProjectState.REVIEW,
            ProjectState.OPTIMIZING,
        },
        ProjectState.ERROR: {
            ProjectState.INITIAL,
            ProjectState.GENERATING_CONTEXT,
            ProjectState.REVIEW,
            ProjectState.APPROVED,
            ProjectState.MANAGED,
            ProjectState.OPTIMIZED,
        },
    }

    @classmethod
    def can_transition(cls, current_state: ProjectState, target_state: ProjectState) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(current_state, set())
        return target_state in allowed

    @classmethod
    def transition(cls, project: Any, target_state: ProjectState, reason: str = "") -> Any:
        if not cls.can_transition(project.state, target_state):
            raise InvalidStateTransitionError(project.state, target_state, reason)

        project.state = target_state
        project.updated_at = datetime.now(timezone.utc).isoformat()
        if target_state == ProjectState.ERROR and reason:
            project.error_message = reason
        elif target_state != ProjectState.ERROR:
            project.error_message = None

        return project
