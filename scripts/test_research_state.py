from app.graph.state_factory import (
    create_initial_state,
    initialize_task_states,
)
from app.graph.task_state import TaskState
from app.graph.workflow_status import WorkflowStatus
from app.schemas.planner import (
    CompletionCriteria,
    ResearchPlan,
    ResearchTaskPlan,
    SourcePolicy,
    TaskType,
)


def build_test_plan() -> ResearchPlan:
    """Create a small deterministic research plan."""

    return ResearchPlan(
        research_goal=(
            "Evaluate AI agents for enterprise research."
        ),
        assumptions=[],
        research_questions=[
            "What are the benefits of AI agents?"
        ],
        tasks=[
            ResearchTaskPlan(
                task_id="task-source-discovery",
                task_type=TaskType.SOURCE_DISCOVERY,
                description="Find relevant sources.",
                research_question=(
                    "What sources discuss AI agents?"
                ),
                expected_outputs=[
                    "source list"
                ],
                dependencies=[],
                required=True,
            ),
            ResearchTaskPlan(
                task_id="task-evidence",
                task_type=TaskType.EVIDENCE_COLLECTION,
                description="Collect evidence.",
                research_question=(
                    "What evidence supports the findings?"
                ),
                expected_outputs=[
                    "evidence"
                ],
                dependencies=[
                    "task-source-discovery"
                ],
                required=True,
            ),
        ],
        source_policy=SourcePolicy(
            allowed_source_types=[
                "web"
            ],
            minimum_sources=2,
            require_independent_sources=True,
            allow_duplicate_sources=False,
        ),
        completion_criteria=CompletionCriteria(
            required_task_ids=[
                "task-source-discovery",
                "task-evidence",
            ],
            minimum_evidence_items=1,
            minimum_verified_claims=1,
        ),
        risk_flags=[],
    )


def main() -> None:
    print()
    print("=" * 70)
    print("RESEARCH STATE TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Create initial state
    # ---------------------------------------------------------

    state = create_initial_state(
        run_id="test-run-001",
        research_goal=(
            "Evaluate AI agents for enterprise research."
        ),
    )

    print()
    print("Initial state:")
    print(f"  Run ID: {state['run_id']}")
    print(f"  Status: {state['status']}")
    print(
        f"  Step count: "
        f"{state['step_count']}"
    )
    print(
        f"  Tool calls: "
        f"{state['tool_call_count']}"
    )
    print(
        f"  Retry count: "
        f"{state['retry_count']}"
    )

    assert (
        state["status"]
        == WorkflowStatus.CREATED.value
    )

    assert state["step_count"] == 0
    assert state["tool_call_count"] == 0
    assert state["retry_count"] == 0

    # ---------------------------------------------------------
    # Initialize task states
    # ---------------------------------------------------------

    plan = build_test_plan()

    state = initialize_task_states(
        state=state,
        plan=plan,
    )

    print()
    print("Task states:")

    for task_id, task_state in (
        state["task_states"].items()
    ):
        print(
            f"  {task_id}: "
            f"{task_state}"
        )

    assert len(
        state["task_states"]
    ) == 2

    assert (
        state["task_states"][
            "task-source-discovery"
        ]
        == TaskState.PENDING.value
    )

    assert (
        state["task_states"][
            "task-evidence"
        ]
        == TaskState.PENDING.value
    )

    assert (
        state["research_plan"]
    )

    print()
    print(
        f"Source IDs: "
        f"{state['source_ids']}"
    )

    print(
        f"Evidence IDs: "
        f"{state['evidence_ids']}"
    )

    print(
        f"Claim IDs: "
        f"{state['claim_ids']}"
    )

    print()
    print("=" * 70)
    print("RESEARCH STATE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()