from enum import Enum
from typing import TypedDict


class TaskState(str, Enum):
    """
    Lifecycle states for a research task.
    """

    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    RETRY_PENDING = "RETRY_PENDING"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"


class ResearchState(TypedDict, total=False):
    run_id: str
    research_goal: str
    research_plan: dict
    task_states: dict[str, str]
    task_retry_counts: dict[str, int]
    completed_tasks: list[str]
    failed_tasks: list[str]
    current_task_ids: list[str]
    source_ids: list[str]
    source_contents: dict[str, str]
    evidence_ids: list[str]
    claim_ids: list[str]
    verified_claim_ids: list[str]
    conflict_ids: list[str]
    step_count: int
    tool_call_count: int
    retry_count: int
    max_steps: int
    max_tool_calls: int
    max_retries: int
    max_search_results: int
    status: str
    error_messages: list[str]