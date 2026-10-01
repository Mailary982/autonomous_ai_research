from app.graph.task_state import TaskState
from app.schemas.planner import ResearchTaskPlan


class DependencyEngine:
    """
    Deterministic dependency engine for research tasks.

    This component determines which tasks are READY based on
    the current state of their dependencies.

    It does not execute tasks and does not use an LLM.
    """

    def get_ready_tasks(
        self,
        tasks: list[ResearchTaskPlan],
        states: dict[str, TaskState],
    ) -> list[ResearchTaskPlan]:
        """
        Return all tasks whose dependencies have completed.

        A task is READY when:

        1. Its current state is PENDING.
        2. Every dependency exists.
        3. Every dependency is COMPLETE.
        """

        if not isinstance(tasks, list):
            raise TypeError(
                "tasks must be a list."
            )

        if not isinstance(states, dict):
            raise TypeError(
                "states must be a dictionary."
            )

        ready_tasks: list[ResearchTaskPlan] = []

        for task in tasks:
            current_state = states.get(
                task.task_id,
                TaskState.PENDING,
            )

            if current_state != TaskState.PENDING:
                continue

            if self._dependencies_satisfied(
                task=task,
                states=states,
            ):
                ready_tasks.append(task)

        return ready_tasks

    def _dependencies_satisfied(
        self,
        task: ResearchTaskPlan,
        states: dict[str, TaskState],
    ) -> bool:
        """
        Determine whether every dependency of a task is complete.
        """

        for dependency_id in task.dependencies:
            if dependency_id not in states:
                raise ValueError(
                    f"Dependency '{dependency_id}' "
                    f"for task '{task.task_id}' "
                    "does not exist."
                )

            if (
                states[dependency_id]
                != TaskState.COMPLETE
            ):
                return False

        return True

    def mark_ready_tasks(
        self,
        tasks: list[ResearchTaskPlan],
        states: dict[str, TaskState],
    ) -> dict[str, TaskState]:
        """
        Update all eligible PENDING tasks to READY.

        A new dictionary is returned so the caller can decide
        whether and when to persist the state.
        """

        updated_states = dict(states)

        ready_tasks = self.get_ready_tasks(
            tasks=tasks,
            states=states,
        )

        for task in ready_tasks:
            updated_states[
                task.task_id
            ] = TaskState.READY

        return updated_states

    def has_unfinished_tasks(
        self,
        tasks: list[ResearchTaskPlan],
        states: dict[str, TaskState],
    ) -> bool:
        """
        Return True when at least one task is not terminal.
        """

        for task in tasks:
            state = states.get(
                task.task_id,
                TaskState.PENDING,
            )

            if state not in {
                TaskState.COMPLETE,
                TaskState.FAILED,
                TaskState.CANCELLED,
                TaskState.BLOCKED,
            }:
                return True

        return False

    def all_required_tasks_complete(
        self,
        tasks: list[ResearchTaskPlan],
        states: dict[str, TaskState],
    ) -> bool:
        """
        Return True when every required task is COMPLETE.
        """

        for task in tasks:
            if not task.required:
                continue

            if (
                states.get(task.task_id)
                != TaskState.COMPLETE
            ):
                return False

        return True