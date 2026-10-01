from typing import Any

from app.graph.dependency_engine import DependencyEngine
from app.graph.recovery import RecoveryController
from app.graph.task_executor import TaskExecutor
from app.graph.task_state import TaskState
from app.graph.workflow_status import WorkflowStatus
from app.schemas.planner import ResearchPlan


class WorkflowNodes:
    """
    LangGraph node implementations.

    Nodes control workflow state transitions.
    Specialist agents perform domain work through TaskExecutor.
    RecoveryController handles bounded task retries.
    """

    def __init__(
        self,
        dependency_engine: DependencyEngine | None = None,
        task_executor: TaskExecutor | None = None,
        recovery_controller: RecoveryController | None = None,
        llm_client: Any | None = None,
    ) -> None:
        self.dependency_engine = (
            dependency_engine
            or DependencyEngine()
        )

        self.task_executor = (
            task_executor
            or TaskExecutor()
        )

        self.recovery_controller = (
            recovery_controller
            or RecoveryController()
        )

        self.llm_client = llm_client

    def plan(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate that a research plan exists and enter PLANNED state.
        """

        plan_data = state.get(
            "research_plan"
        )

        if not plan_data:
            raise ValueError(
                "research_plan is required before planning."
            )

        self._get_plan(
            state
        )

        state["status"] = (
            WorkflowStatus.PLANNED.value
        )

        state["step_count"] = (
            state.get(
                "step_count",
                0,
            )
            + 1
        )

        return state

    def schedule(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Schedule dependency-ready tasks and recover failed tasks.

        Scheduling responsibilities:

        1. Convert RETRY_PENDING tasks back to READY.
        2. Detect permanently failed dependencies.
        3. Block tasks that can no longer execute.
        4. Convert eligible PENDING tasks to READY.
        5. Populate current_task_ids.
        """

        self._check_execution_limits(
            state
        )

        plan = self._get_plan(
            state
        )

        task_states = {
            task_id: TaskState(task_state)
            for task_id, task_state
            in state.get(
                "task_states",
                {},
            ).items()
        }

        retry_counts = state.setdefault(
            "task_retry_counts",
            {},
        )

        # -----------------------------------------------------
        # 1. FAILED → RETRY_PENDING / FAILED
        # -----------------------------------------------------

        for task in plan.tasks:
            task_state = task_states.get(
                task.task_id,
                TaskState.PENDING,
            )

            if task_state != TaskState.FAILED:
                continue

            retry_count = retry_counts.get(
                task.task_id,
                0,
            )

            decision = (
                self.recovery_controller.evaluate_failure(
                    task_id=task.task_id,
                    task_state=TaskState.FAILED,
                    retry_count=retry_count,
                )
            )

            retry_counts[
                task.task_id
            ] = decision.retry_count

            if decision.should_retry:
                task_states[
                    task.task_id
                ] = TaskState.RETRY_PENDING

        # -----------------------------------------------------
        # 2. RETRY_PENDING → READY
        # -----------------------------------------------------

        for task in plan.tasks:
            if (
                task_states.get(task.task_id)
                == TaskState.RETRY_PENDING
            ):
                task_states[
                    task.task_id
                ] = TaskState.READY

        # -----------------------------------------------------
        # 3. Block tasks whose dependencies permanently failed
        # -----------------------------------------------------

        changed = True

        while changed:
            changed = False

            for task in plan.tasks:
                current_state = task_states.get(
                    task.task_id,
                    TaskState.PENDING,
                )

                if current_state not in {
                    TaskState.PENDING,
                    TaskState.READY,
                }:
                    continue

                dependency_states = [
                    task_states.get(
                        dependency_id,
                        TaskState.PENDING,
                    )
                    for dependency_id in task.dependencies
                ]

                if not dependency_states:
                    continue

                if (
                    self.recovery_controller
                    .should_block_dependent_task(
                        dependency_states
                    )
                ):
                    task_states[
                        task.task_id
                    ] = TaskState.BLOCKED

                    changed = True

        # -----------------------------------------------------
        # 4. PENDING → READY
        # -----------------------------------------------------

        task_states = (
            self.dependency_engine.mark_ready_tasks(
                tasks=plan.tasks,
                states=task_states,
            )
        )

        # -----------------------------------------------------
        # 5. Persist task states
        # -----------------------------------------------------

        state["task_states"] = {
            task_id: task_state.value
            for task_id, task_state
            in task_states.items()
        }

        # -----------------------------------------------------
        # 6. Select READY tasks
        # -----------------------------------------------------

        ready_tasks = [
            task
            for task in plan.tasks
            if task_states.get(task.task_id)
            == TaskState.READY
        ]

        state["current_task_ids"] = [
            task.task_id
            for task in ready_tasks
        ]

        # -----------------------------------------------------
        # 7. Determine workflow status
        # -----------------------------------------------------

        all_terminal = all(
            task_states.get(
                task.task_id,
                TaskState.PENDING,
            )
            in {
                TaskState.COMPLETE,
                TaskState.FAILED,
                TaskState.CANCELLED,
                TaskState.BLOCKED,
            }
            for task in plan.tasks
        )

        if all_terminal:
            state["status"] = (
                WorkflowStatus.COMPLETED.value
            )
        else:
            state["status"] = (
                WorkflowStatus.EXECUTING.value
            )

        state["step_count"] = (
            state.get(
                "step_count",
                0,
            )
            + 1
        )

        return state

    def execute_tasks(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute currently scheduled tasks.

        State transition:

            READY
              ↓
            RUNNING
              ↓
           VERIFYING
              ↓
           COMPLETE

        On exception:

            RUNNING
              ↓
            FAILED

        Recovery is handled by the next scheduling cycle.
        """

        self._check_execution_limits(
            state
        )

        plan = self._get_plan(
            state
        )

        task_lookup = {
            task.task_id: task
            for task in plan.tasks
        }

        current_task_ids = state.get(
            "current_task_ids",
            [],
        )

        for task_id in current_task_ids:
            task = task_lookup.get(
                task_id
            )

            if task is None:
                raise ValueError(
                    f"Task not found: {task_id}"
                )

            current_state = TaskState(
                state["task_states"][task_id]
            )

            if current_state != TaskState.READY:
                continue

            state["task_states"][
                task_id
            ] = TaskState.RUNNING.value

            try:
                result = (
                    self.task_executor.execute(
                        task,
                        state,
                    )
                )

                if not isinstance(
                    result,
                    dict,
                ):
                    raise TypeError(
                        "Task executor must return a dictionary."
                    )

                state["task_states"][
                    task_id
                ] = TaskState.VERIFYING.value

                self._merge_task_result(
                    state,
                    result,
                )

                state["task_states"][
                    task_id
                ] = TaskState.COMPLETE.value

                completed_tasks = state.setdefault(
                    "completed_tasks",
                    [],
                )

                if task_id not in completed_tasks:
                    completed_tasks.append(
                        task_id
                    )

            except Exception as exc:
                state["task_states"][
                    task_id
                ] = TaskState.FAILED.value

                failed_tasks = state.setdefault(
                    "failed_tasks",
                    [],
                )

                if task_id not in failed_tasks:
                    failed_tasks.append(
                        task_id
                    )

                errors = state.setdefault(
                    "error_messages",
                    [],
                )

                errors.append(
                    f"Task {task_id} failed: {exc}"
                )

        state["current_task_ids"] = []

        state["step_count"] = (
            state.get(
                "step_count",
                0,
            )
            + 1
        )

        return state

    def finalize(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Finalize the workflow.
        """

        task_states = state.get(
            "task_states",
            {},
        )

        if any(
            task_state
            == TaskState.FAILED.value
            for task_state in task_states.values()
        ):
            state["status"] = (
                WorkflowStatus.FAILED.value
            )

        elif any(
            task_state
            == TaskState.BLOCKED.value
            for task_state in task_states.values()
        ):
            state["status"] = (
                WorkflowStatus.BLOCKED.value
            )

        else:
            state["status"] = (
                WorkflowStatus.COMPLETED.value
            )

        state["step_count"] = (
            state.get(
                "step_count",
                0,
            )
            + 1
        )

        return state

    def _merge_task_result(
        self,
        state: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """
        Merge specialist-agent outputs into workflow state.
        """

        for field in (
            "source_ids",
            "evidence_ids",
            "claim_ids",
            "verified_claim_ids",
            "conflict_ids",
        ):
            values = result.get(
                field,
                [],
            )

            if not isinstance(
                values,
                list,
            ):
                raise TypeError(
                    f"{field} must be a list."
                )

            target = state.setdefault(
                field,
                [],
            )

            for value in values:
                if value not in target:
                    target.append(
                        value
                    )

        source_contents = result.get(
            "source_contents",
            {},
        )

        if not isinstance(
            source_contents,
            dict,
        ):
            raise TypeError(
                "source_contents must be a dictionary."
            )

        target_contents = state.setdefault(
            "source_contents",
            {},
        )

        for source_id, content in source_contents.items():
            if not isinstance(
                source_id,
                str,
            ):
                raise TypeError(
                    "source content IDs must be strings."
                )

            if not isinstance(
                content,
                str,
            ):
                raise TypeError(
                    "source contents must be strings."
                )

            target_contents[
                source_id
            ] = content

        tool_calls = result.get(
            "tool_calls",
            0,
        )

        if not isinstance(
            tool_calls,
            int,
        ):
            raise TypeError(
                "tool_calls must be an integer."
            )

        if tool_calls < 0:
            raise ValueError(
                "tool_calls cannot be negative."
            )

        state["tool_call_count"] = (
            state.get(
                "tool_call_count",
                0,
            )
            + tool_calls
        )

    @staticmethod
    def _get_plan(
        state: dict[str, Any],
    ) -> ResearchPlan:
        """
        Validate and return the research plan.
        """

        plan_data = state.get(
            "research_plan"
        )

        if not plan_data:
            raise ValueError(
                "research_plan is missing."
            )

        if isinstance(
            plan_data,
            ResearchPlan,
        ):
            return plan_data

        return ResearchPlan.model_validate(
            plan_data
        )

    @staticmethod
    def _check_execution_limits(
        state: dict[str, Any],
    ) -> None:
        """
        Enforce bounded workflow execution.
        """

        if (
            state.get(
                "step_count",
                0,
            )
            >= state.get(
                "max_steps",
                50,
            )
        ):
            raise RuntimeError(
                "Maximum workflow step limit reached."
            )

        if (
            state.get(
                "tool_call_count",
                0,
            )
            >= state.get(
                "max_tool_calls",
                100,
            )
        ):
            raise RuntimeError(
                "Maximum tool-call limit reached."
            )