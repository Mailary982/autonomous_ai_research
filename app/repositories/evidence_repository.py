from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evidence import Evidence


class EvidenceRepository:
    """Persistence operations for research evidence."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        source_id: str,
        locator: str | None,
        excerpt: str,
        captured_at: datetime,
        evidence_quality: float | None,
    ) -> Evidence:
        """Create and persist a new evidence record."""

        evidence = Evidence(
            source_id=source_id,
            locator=locator,
            excerpt=excerpt,
            captured_at=captured_at,
            evidence_quality=evidence_quality,
        )

        self.session.add(evidence)
        self.session.flush()

        return evidence

    def get_by_source_id(
        self,
        source_id: str,
    ) -> list[Evidence]:
        """Return all evidence associated with a source."""

        statement = (
            select(Evidence)
            .where(Evidence.source_id == source_id)
            .order_by(Evidence.captured_at)
        )

        return list(
            self.session.scalars(statement).all()
        )