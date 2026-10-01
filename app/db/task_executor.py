from collections.abc import Callable
from typing import Any

from app.graph.task_state import TaskState
from app.schemas.planner import ResearchTaskPlan, TaskType


class TaskExecutor:
    """
    Dispatches planned research tasks to the appropriate specialist agent.

    The executor is intentionally deterministic:
    - The Planner decides WHAT tasks are required.
    - The Orchestrator decides WHEN a task can run.
    - The TaskExecutor decides WHICH agent handles the task.
    - Specialist agents perform the actual work.
    """

    def __init__(
        self,
        agents: dict[TaskType, Any] | None = None,
    ) -> None:
        self.agents = agents or {}

    def register_agent(
        self,
        task_type: TaskType,
        agent: Any,
    ) -> None:
        """
        Register a specialist agent for a task type.
        """

        if not isinstance(task_type, TaskType):
            raise TypeError(
                "task_type must be an instance of TaskType."
            )

        if agent is None:
            raise ValueError(
                "agent cannot be None."
            )

        self.agents[task_type] = agent

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute one planned task using its registered specialist agent.
        """

        if not isinstance(task, ResearchTaskPlan):
            raise TypeError(
                "task must be a ResearchTaskPlan."
            )

        task_type = task.task_type

        if task_type not in self.agents:
            raise RuntimeError(
                f"No agent registered for task type: "
                f"{task_type.value}"
            )

        agent = self.agents[task_type]

        if not hasattr(agent, "execute"):
            raise TypeError(
                f"Agent registered for {task_type.value} "
                "must provide an execute() method."
            )

        return agent.execute(
            task=task,
            state=state,
        )

    def execute_ready_tasks(
        self,
        tasks: list[ResearchTaskPlan],
        task_states: dict[str, TaskState],
        state: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """
        Execute all READY tasks.

        Returns:
            Mapping of task_id -> task execution result.
        """

        results: dict[str, dict[str, Any]] = {}

        for task in tasks:
            current_state = task_states.get(
                task.task_id
            )

            if current_state != TaskState.READY:
                continue

            result = self.execute(
                task=task,
                state=state,
            )

            results[task.task_id] = result

        return results