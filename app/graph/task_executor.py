from typing import Any

from app.graph.task_state import TaskState
from app.schemas.planner import ResearchTaskPlan, TaskType


class TaskExecutor:
    """
    Dispatches planned research tasks to the appropriate specialist agent.

    Architecture:
        Planner -> LangGraph -> TaskExecutor -> Specialist Agent

    The executor does not decide what research should be done.
    It only dispatches an already-planned task to the correct agent.
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
        """Register a specialist agent for a task type."""

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
        """Execute one planned task using its registered agent."""

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
        Execute every task currently in READY state.

        Returns:
            Dictionary mapping task IDs to execution results.
        """

        results: dict[str, dict[str, Any]] = {}

        for task in tasks:
            current_state = task_states.get(task.task_id)

            if current_state != TaskState.READY:
                continue

            result = self.execute(
                task=task,
                state=state,
            )

            results[task.task_id] = result

        return results