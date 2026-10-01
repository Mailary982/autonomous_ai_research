from app.graph.state import ResearchState
from app.graph.task_state import TaskState
from app.graph.workflow_status import WorkflowStatus
from app.schemas.planner import ResearchPlan


def create_initial_state(
    *,
    run_id: str,
    research_goal: str,
    max_steps: int = 50,
    max_tool_calls: int = 100,
    max_retries: int = 3,
) -> ResearchState:
    """
    Create the initial state for a research workflow.
    """

    if not run_id.strip():
        raise ValueError(
            "run_id cannot be empty."
        )

    if not research_goal.strip():
        raise ValueError(
            "research_goal cannot be empty."
        )

    if max_steps < 1:
        raise ValueError(
            "max_steps must be at least 1."
        )

    if max_tool_calls < 1:
        raise ValueError(
            "max_tool_calls must be at least 1."
        )

    if max_retries < 0:
        raise ValueError(
            "max_retries cannot be negative."
        )

    return ResearchState(
        run_id=run_id,
        research_goal=research_goal,
        research_plan={},
        task_states={},
        completed_tasks=[],
        failed_tasks=[],
        current_task_ids=[],
        source_ids=[],
        evidence_ids=[],
        claim_ids=[],
        conflict_ids=[],
        step_count=0,
        tool_call_count=0,
        retry_count=0,
        max_steps=max_steps,
        max_tool_calls=max_tool_calls,
        max_retries=max_retries,
        status=WorkflowStatus.CREATED.value,
        error_messages=[],
    )


def initialize_task_states(
    state: ResearchState,
    plan: ResearchPlan,
) -> ResearchState:
    """
    Add task states from a validated ResearchPlan.
    """

    task_states = {
        task.task_id: TaskState.PENDING.value
        for task in plan.tasks
    }

    updated_state = dict(state)

    updated_state["research_plan"] = (
        plan.model_dump()
    )

    updated_state["task_states"] = task_states

    return ResearchState(**updated_state)