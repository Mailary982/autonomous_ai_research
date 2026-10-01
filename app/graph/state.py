from app.graph.task_state import ResearchState


def create_initial_state(
    run_id: str,
    research_goal: str,
    *,
    max_steps: int = 50,
    max_tool_calls: int = 100,
    max_retries: int = 3,
    max_search_results: int = 3,
) -> ResearchState:
    """
    Create bounded initial workflow state.
    """

    if not run_id.strip():
        raise ValueError(
            "run_id cannot be empty."
        )

    if not research_goal.strip():
        raise ValueError(
            "research_goal cannot be empty."
        )

    if max_steps <= 0:
        raise ValueError(
            "max_steps must be positive."
        )

    if max_tool_calls <= 0:
        raise ValueError(
            "max_tool_calls must be positive."
        )

    if max_retries < 0:
        raise ValueError(
            "max_retries cannot be negative."
        )

    if not 1 <= max_search_results <= 10:
        raise ValueError(
            "max_search_results must be between 1 and 10."
        )

    return ResearchState(
        run_id=run_id,
        research_goal=research_goal,
        research_plan={},
        task_states={},
        task_retry_counts={},
        completed_tasks=[],
        failed_tasks=[],
        current_task_ids=[],
        source_ids=[],
        source_contents={},
        evidence_ids=[],
        claim_ids=[],
        verified_claim_ids=[],
        conflict_ids=[],
        step_count=0,
        tool_call_count=0,
        retry_count=0,
        max_steps=max_steps,
        max_tool_calls=max_tool_calls,
        max_retries=max_retries,
        max_search_results=max_search_results,
        status="CREATED",
        error_messages=[],
    )


def initialize_task_states(
    state: ResearchState,
    plan,
) -> ResearchState:
    """
    Attach planner output and initialize all tasks as PENDING.
    """

    task_states = {
        task.task_id: "PENDING"
        for task in plan.tasks
    }

    task_retry_counts = {
        task.task_id: 0
        for task in plan.tasks
    }

    state["research_plan"] = plan.model_dump()

    state["task_states"] = task_states

    state["task_retry_counts"] = task_retry_counts

    state["status"] = "PLANNED"

    return state