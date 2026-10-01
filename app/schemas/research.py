from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.research_run import ResearchRunStatus
from app.models.research_task import ResearchTaskStatus


class ResearchRunCreate(BaseModel):
    """Request payload for creating a research run."""

    objective: str = Field(
        ...,
        min_length=10,
        description="The research objective or question to investigate.",
    )

    constraints: list[str] = Field(
        default_factory=list,
        description="Optional constraints that should guide the research.",
    )

    output_format: str = Field(
        default="report",
        description="Requested output format.",
    )


class ResearchTaskResponse(BaseModel):
    """API representation of a research task."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    parent_id: UUID | None
    task_type: str
    description: str
    dependencies: str | None
    status: ResearchTaskStatus
    retry_count: int
    max_retries: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ResearchRunResponse(BaseModel):
    """API representation of a research run."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    objective: str
    constraints: str | None
    output_format: str
    status: ResearchRunStatus
    config_version: str
    error_message: str | None
    cost: int
    created_at: datetime
    updated_at: datetime


class ResearchRunDetailResponse(ResearchRunResponse):
    """Research run with its associated tasks."""

    tasks: list[ResearchTaskResponse] = Field(default_factory=list)