from dataclasses import dataclass

from app.graph.task_state import TaskState


@dataclass(frozen=True)
class RetryDecision:
    """
    Result of evaluating whether a failed task should retry.
    """

    state: TaskState
    should_retry: bool
    retry_count: int
    reason: str


class RecoveryController:
    """
    Controls bounded task retry and failure transitions.

    This component is deterministic and does not use an LLM.

    Responsibilities:
    - determine whether a failed task may retry
    - enforce the retry budget
    - transition FAILED -> RETRY_PENDING
    - identify permanently failed tasks
    """

    def __init__(
        self,
        max_retries: int = 3,
    ) -> None:
        if max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )

        self.max_retries = max_retries

    def evaluate_failure(
        self,
        *,
        task_id: str,
        task_state: TaskState,
        retry_count: int,
    ) -> RetryDecision:
        """
        Evaluate a failed task and determine whether it can retry.
        """

        if not task_id.strip():
            raise ValueError(
                "task_id cannot be empty."
            )

        if not isinstance(
            task_state,
            TaskState,
        ):
            raise TypeError(
                "task_state must be a TaskState."
            )

        if retry_count < 0:
            raise ValueError(
                "retry_count cannot be negative."
            )

        if task_state != TaskState.FAILED:
            raise ValueError(
                "Recovery evaluation requires a FAILED task."
            )

        if retry_count < self.max_retries:
            return RetryDecision(
                state=TaskState.RETRY_PENDING,
                should_retry=True,
                retry_count=retry_count + 1,
                reason=(
                    f"Task '{task_id}' failed but remains "
                    f"within the retry budget."
                ),
            )

        return RetryDecision(
            state=TaskState.FAILED,
            should_retry=False,
            retry_count=retry_count,
            reason=(
                f"Task '{task_id}' exhausted the maximum "
                f"retry budget of {self.max_retries}."
            ),
        )

    def should_block_dependent_task(
        self,
        dependency_states: list[TaskState],
    ) -> bool:
        """
        Determine whether a dependent task must be blocked.

        A dependent task is blocked when at least one dependency
        has permanently failed or has been cancelled/blocked.
        """

        if not isinstance(
            dependency_states,
            list,
        ):
            raise TypeError(
                "dependency_states must be a list."
            )

        terminal_blocking_states = {
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.BLOCKED,
        }

        return any(
            state in terminal_blocking_states
            for state in dependency_states
        )