from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Evidence(Base):
    """A specific piece of evidence extracted from a source."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    locator: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    excerpt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    evidence_quality: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )