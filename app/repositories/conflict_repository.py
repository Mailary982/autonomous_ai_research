from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conflict import Conflict


class ConflictRepository:
    """Persistence operations for detected conflicts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        claim_id: str,
        supporting_evidence_id: str,
        contradicting_evidence_id: str,
        detected_at: datetime,
    ) -> Conflict:
        """Persist a newly detected conflict."""

        conflict = Conflict(
            claim_id=claim_id,
            supporting_evidence_id=supporting_evidence_id,
            contradicting_evidence_id=contradicting_evidence_id,
            detected_at=detected_at,
        )

        self.session.add(conflict)
        self.session.flush()

        return conflict

    def get_by_claim_id(
        self,
        claim_id: str,
    ) -> list[Conflict]:
        """Return all conflicts associated with a claim."""

        statement = (
            select(Conflict)
            .where(Conflict.claim_id == claim_id)
            .order_by(Conflict.detected_at)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def update_resolution(
        self,
        *,
        conflict_id: str,
        resolution_status: str,
        preferred_evidence_id: str | None,
        confidence: float,
        reasoning: str,
    ) -> Conflict:
        """Persist the resolution of a conflict."""

        statement = select(Conflict).where(
            Conflict.id == conflict_id
        )

        conflict = self.session.scalar(statement)

        if conflict is None:
            raise ValueError(
                f"Conflict not found: {conflict_id}"
            )

        conflict.resolution_status = resolution_status
        conflict.preferred_evidence_id = (
            preferred_evidence_id
        )
        conflict.confidence = confidence
        conflict.reasoning = reasoning

        self.session.flush()

        return conflict