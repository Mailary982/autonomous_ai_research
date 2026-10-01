from enum import Enum
from uuid import uuid4

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClaimStatus(str, Enum):
    """Verification state of a factual claim."""

    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONFLICTED = "CONFLICTED"
    UNSUPPORTED = "UNSUPPORTED"
    OUTDATED = "OUTDATED"


class Claim(Base):
    """A factual statement produced during research."""

    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ClaimStatus] = mapped_column(
        SQLEnum(ClaimStatus),
        nullable=False,
        default=ClaimStatus.UNSUPPORTED,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )