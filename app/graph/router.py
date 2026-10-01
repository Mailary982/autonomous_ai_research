from app.graph.state import ResearchState
from app.graph.task_state import TaskState
from app.graph.workflow_status import WorkflowStatus


class WorkflowRouter:
    """
    Deterministic routing logic for the research workflow.

    The router decides what happens next based on workflow
    state. It does not use an LLM.
    """

    def route_after_schedule(
        self,
        state: ResearchState,
    ) -> str:
        """
        Decide whether to execute tasks or finalize.

        Returns:

            "execute_tasks"
            "finalize"
        """

        current_task_ids = state.get(
            "current_task_ids",
            [],
        )

        if current_task_ids:
            return "execute_tasks"

        task_states = state.get(
            "task_states",
            {},
        )

        if not task_states:
            return "finalize"

        all_terminal = all(
            TaskState(task_state)
            in {
                TaskState.COMPLETE,
                TaskState.FAILED,
                TaskState.CANCELLED,
                TaskState.BLOCKED,
            }
            for task_state in task_states.values()
        )

        if all_terminal:
            return "finalize"

        raise RuntimeError(
            "No READY tasks are available, "
            "but the workflow is not terminal."
        )

    def route_after_execution(
        self,
        state: ResearchState,
    ) -> str:
        """
        Decide whether to schedule another batch or finalize.
        """

        task_states = state.get(
            "task_states",
            {},
        )

        if not task_states:
            return "finalize"

        all_terminal = all(
            TaskState(task_state)
            in {
                TaskState.COMPLETE,
                TaskState.FAILED,
                TaskState.CANCELLED,
                TaskState.BLOCKED,
            }
            for task_state in task_states.values()
        )

        if all_terminal:
            return "finalize"

        return "schedule"

    def route_after_plan(
        self,
        state: ResearchState,
    ) -> str:
        """
        Route from planning into execution.
        """

        if state.get("status") == (
            WorkflowStatus.FAILED.value
        ):
            return "finalize"

        return "schedule"