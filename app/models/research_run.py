import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.research_task import ResearchTask


class ResearchRunStatus(str, enum.Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"


class ResearchRun(Base):
    __tablename__ = "research_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    constraints: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    output_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="markdown",
    )

    status: Mapped[ResearchRunStatus] = mapped_column(
        Enum(ResearchRunStatus, name="research_run_status"),
        nullable=False,
        default=ResearchRunStatus.PENDING,
    )

    config_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="v1",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cost: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tasks: Mapped[list["ResearchTask"]] = relationship(
        "ResearchTask",
        back_populates="run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )