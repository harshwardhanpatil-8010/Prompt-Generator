import pytest
from backend.models import Project
from backend.state_machine import (
    InvalidStateTransitionError,
    ProjectState,
    ProjectStateMachine,
)


def test_valid_state_transitions():
    project = Project(
        project_id="test-123",
        state=ProjectState.INITIAL,
        original_prompt="Test sneaker website prompt",
    )

    # INITIAL -> GENERATING_CONTEXT
    ProjectStateMachine.transition(project, ProjectState.GENERATING_CONTEXT)
    assert project.state == ProjectState.GENERATING_CONTEXT

    # GENERATING_CONTEXT -> CONTEXT_READY
    ProjectStateMachine.transition(project, ProjectState.CONTEXT_READY)
    assert project.state == ProjectState.CONTEXT_READY

    # CONTEXT_READY -> APPROVED
    ProjectStateMachine.transition(project, ProjectState.APPROVED)
    assert project.state == ProjectState.APPROVED

    # APPROVED -> MANAGED
    ProjectStateMachine.transition(project, ProjectState.MANAGED)
    assert project.state == ProjectState.MANAGED

    # MANAGED -> OPTIMIZING
    ProjectStateMachine.transition(project, ProjectState.OPTIMIZING)
    assert project.state == ProjectState.OPTIMIZING

    # OPTIMIZING -> OPTIMIZED
    ProjectStateMachine.transition(project, ProjectState.OPTIMIZED)
    assert project.state == ProjectState.OPTIMIZED

    # OPTIMIZED -> FINAL_PROMPT_READY
    ProjectStateMachine.transition(project, ProjectState.FINAL_PROMPT_READY)
    assert project.state == ProjectState.FINAL_PROMPT_READY


def test_invalid_state_transition_raises():
    project = Project(
        project_id="test-456",
        state=ProjectState.INITIAL,
        original_prompt="Test project prompt",
    )

    # Cannot jump directly from INITIAL to FINAL_PROMPT_READY
    with pytest.raises(InvalidStateTransitionError):
        ProjectStateMachine.transition(project, ProjectState.FINAL_PROMPT_READY)

    # Cannot jump directly from INITIAL to OPTIMIZED
    with pytest.raises(InvalidStateTransitionError):
        ProjectStateMachine.transition(project, ProjectState.OPTIMIZED)
