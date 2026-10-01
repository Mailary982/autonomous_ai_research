from app.agents.mock_agent import MockResearchAgent
from app.graph.task_executor import TaskExecutor
from app.graph.task_state import TaskState
from app.schemas.planner import (
    ResearchTaskPlan,
    TaskType,
)


def build_task(
    task_id: str,
    task_type: TaskType,
) -> ResearchTaskPlan:
    return ResearchTaskPlan(
        task_id=task_id,
        task_type=task_type,
        description=f"Execute {task_type.value}",
        research_question="What are AI research agents?",
        expected_outputs=["result"],
        dependencies=[],
        required=True,
    )


def main() -> None:
    print("TASK EXECUTOR TEST")
    print("-" * 40)

    researcher = MockResearchAgent(
        agent_name="researcher"
    )

    verifier = MockResearchAgent(
        agent_name="verifier"
    )

    executor = TaskExecutor()

    executor.register_agent(
        TaskType.SOURCE_DISCOVERY,
        researcher,
    )

    executor.register_agent(
        TaskType.VERIFICATION,
        verifier,
    )

    discovery_task = build_task(
        "task-discovery",
        TaskType.SOURCE_DISCOVERY,
    )

    verification_task = build_task(
        "task-verification",
        TaskType.VERIFICATION,
    )

    task_states = {
        "task-discovery": TaskState.READY,
        "task-verification": TaskState.READY,
    }

    tasks = [
        discovery_task,
        verification_task,
    ]

    results = executor.execute_ready_tasks(
        tasks=tasks,
        task_states=task_states,
        state={
            "research_goal": "Test research workflow",
        },
    )

    assert len(results) == 2

    assert results["task-discovery"]["agent"] == "researcher"

    assert results["task-verification"]["agent"] == "verifier"

    assert (
        researcher.execution_count == 1
    )

    assert (
        verifier.execution_count == 1
    )

    print(
        "Discovery agent:",
        results["task-discovery"]["agent"],
    )

    print(
        "Verification agent:",
        results["task-verification"]["agent"],
    )

    print(
        "Researcher executions:",
        researcher.execution_count,
    )

    print(
        "Verifier executions:",
        verifier.execution_count,
    )

    print()
    print("TASK EXECUTOR TEST PASSED")


if __name__ == "__main__":
    main()