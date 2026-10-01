from app.graph.recovery import RecoveryController
from app.graph.task_state import TaskState


def main() -> None:
    print("=" * 75)
    print("RECOVERY CONTROLLER TEST")
    print("=" * 75)

    controller = RecoveryController(
        max_retries=3
    )

    # ---------------------------------------------------------
    # Test 1: first failure should retry
    # ---------------------------------------------------------

    decision = controller.evaluate_failure(
        task_id="task-a",
        task_state=TaskState.FAILED,
        retry_count=0,
    )

    assert decision.should_retry is True
    assert decision.state == TaskState.RETRY_PENDING
    assert decision.retry_count == 1

    print("First failure → RETRY_PENDING: PASS")

    # ---------------------------------------------------------
    # Test 2: second failure should retry
    # ---------------------------------------------------------

    decision = controller.evaluate_failure(
        task_id="task-a",
        task_state=TaskState.FAILED,
        retry_count=1,
    )

    assert decision.should_retry is True
    assert decision.state == TaskState.RETRY_PENDING
    assert decision.retry_count == 2

    print("Second failure → RETRY_PENDING: PASS")

    # ---------------------------------------------------------
    # Test 3: third failure should retry
    # ---------------------------------------------------------

    decision = controller.evaluate_failure(
        task_id="task-a",
        task_state=TaskState.FAILED,
        retry_count=2,
    )

    assert decision.should_retry is True
    assert decision.state == TaskState.RETRY_PENDING
    assert decision.retry_count == 3

    print("Third failure → RETRY_PENDING: PASS")

    # ---------------------------------------------------------
    # Test 4: retry budget exhausted
    # ---------------------------------------------------------

    decision = controller.evaluate_failure(
        task_id="task-a",
        task_state=TaskState.FAILED,
        retry_count=3,
    )

    assert decision.should_retry is False
    assert decision.state == TaskState.FAILED
    assert decision.retry_count == 3

    print("Retry budget exhausted → FAILED: PASS")

    # ---------------------------------------------------------
    # Test 5: dependency failure blocks dependent task
    # ---------------------------------------------------------

    should_block = (
        controller.should_block_dependent_task(
            [
                TaskState.COMPLETE,
                TaskState.FAILED,
            ]
        )
    )

    assert should_block is True

    print(
        "Failed dependency → BLOCK dependent: PASS"
    )

    # ---------------------------------------------------------
    # Test 6: all dependencies healthy
    # ---------------------------------------------------------

    should_block = (
        controller.should_block_dependent_task(
            [
                TaskState.COMPLETE,
                TaskState.COMPLETE,
            ]
        )
    )

    assert should_block is False

    print(
        "All dependencies complete → no block: PASS"
    )

    print()
    print("=" * 75)
    print("RECOVERY CONTROLLER TEST PASSED")
    print("=" * 75)


if __name__ == "__main__":
    main()