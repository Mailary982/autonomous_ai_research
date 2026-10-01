from enum import Enum


class WorkflowStatus(str, Enum):
    """Lifecycle states for an entire research run."""

    CREATED = "CREATED"

    PLANNING = "PLANNING"
    PLANNED = "PLANNED"

    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    SYNTHESIZING = "SYNTHESIZING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"