from app.graph.dependency_engine import DependencyEngine
from app.graph.task_state import TaskState
from app.schemas.planner import (
    ResearchTaskPlan,
    TaskType,
)


def build_tasks() -> list[ResearchTaskPlan]:
    """Create a deterministic task graph for testing."""

    return [
        ResearchTaskPlan(
            task_id="task-a",
            task_type=TaskType.SOURCE_DISCOVERY,
            description="Discover sources.",
            research_question="Find relevant sources.",
            expected_outputs=[
                "sources"
            ],
            dependencies=[],
            required=True,
        ),
        ResearchTaskPlan(
            task_id="task-b",
            task_type=TaskType.EVIDENCE_COLLECTION,
            description="Collect evidence.",
            research_question="Collect relevant evidence.",
            expected_outputs=[
                "evidence"
            ],
            dependencies=[
                "task-a"
            ],
            required=True,
        ),
        ResearchTaskPlan(
            task_id="task-c",
            task_type=TaskType.ANALYSIS,
            description="Analyze evidence.",
            research_question="Analyze collected evidence.",
            expected_outputs=[
                "analysis"
            ],
            dependencies=[
                "task-b"
            ],
            required=True,
        ),
        ResearchTaskPlan(
            task_id="task-d",
            task_type=TaskType.VERIFICATION,
            description="Verify claims.",
            research_question="Verify research claims.",
            expected_outputs=[
                "verified claims"
            ],
            dependencies=[
                "task-b",
                "task-c",
            ],
            required=True,
        ),
        ResearchTaskPlan(
            task_id="task-e",
            task_type=TaskType.SYNTHESIS,
            description="Synthesize findings.",
            research_question="Create final synthesis.",
            expected_outputs=[
                "final report"
            ],
            dependencies=[
                "task-d"
            ],
            required=True,
        ),
    ]


def main() -> None:
    tasks = build_tasks()

    engine = DependencyEngine()

    states = {
        task.task_id: TaskState.PENDING
        for task in tasks
    }

    print()
    print("=" * 70)
    print("DEPENDENCY ENGINE TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Initial state
    # ---------------------------------------------------------

    states = engine.mark_ready_tasks(
        tasks=tasks,
        states=states,
    )

    assert (
        states["task-a"]
        == TaskState.READY
    )

    assert (
        states["task-b"]
        == TaskState.PENDING
    )

    print()
    print("Initial ready task:")

    for task_id, state in states.items():
        if state == TaskState.READY:
            print(f"  - {task_id}")

    # ---------------------------------------------------------
    # Complete task A
    # ---------------------------------------------------------

    states["task-a"] = TaskState.COMPLETE

    states = engine.mark_ready_tasks(
        tasks=tasks,
        states=states,
    )

    assert (
        states["task-b"]
        == TaskState.READY
    )

    print()
    print("After task-a completes:")

    for task_id, state in states.items():
        if state == TaskState.READY:
            print(f"  - {task_id}")

    # ---------------------------------------------------------
    # Complete task B
    # ---------------------------------------------------------

    states["task-b"] = TaskState.COMPLETE

    states = engine.mark_ready_tasks(
        tasks=tasks,
        states=states,
    )

    assert (
        states["task-c"]
        == TaskState.READY
    )

    assert (
        states["task-d"]
        == TaskState.PENDING
    )

    print()
    print("After task-b completes:")

    for task_id, state in states.items():
        if state == TaskState.READY:
            print(f"  - {task_id}")

    # ---------------------------------------------------------
    # Complete task C
    # ---------------------------------------------------------

    states["task-c"] = TaskState.COMPLETE

    states = engine.mark_ready_tasks(
        tasks=tasks,
        states=states,
    )

    assert (
        states["task-d"]
        == TaskState.READY
    )

    print()
    print("After task-c completes:")

    for task_id, state in states.items():
        if state == TaskState.READY:
            print(f"  - {task_id}")

    # ---------------------------------------------------------
    # Complete task D
    # ---------------------------------------------------------

    states["task-d"] = TaskState.COMPLETE

    states = engine.mark_ready_tasks(
        tasks=tasks,
        states=states,
    )

    assert (
        states["task-e"]
        == TaskState.READY
    )

    print()
    print("After task-d completes:")

    for task_id, state in states.items():
        if state == TaskState.READY:
            print(f"  - {task_id}")

    # ---------------------------------------------------------
    # Complete task E
    # ---------------------------------------------------------

    states["task-e"] = TaskState.COMPLETE

    assert engine.all_required_tasks_complete(
        tasks=tasks,
        states=states,
    )

    assert not engine.has_unfinished_tasks(
        tasks=tasks,
        states=states,
    )

    print()
    print("Final states:")

    for task_id, state in states.items():
        print(
            f"  {task_id}: {state.value}"
        )

    print()
    print("=" * 70)
    print("DEPENDENCY ENGINE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()