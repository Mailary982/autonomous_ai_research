from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.conflict_detector import (
    ConflictDetector,
    EvidenceRelationship,
)
from app.agents.conflict_resolver import ConflictResolver
from app.models.conflict import Conflict
from app.repositories.conflict_repository import (
    ConflictRepository,
)
from app.schemas.conflict import ConflictResolution


class ConflictService:
    """Application service for conflict detection and resolution."""

    def __init__(
        self,
        session: Session,
        detector: ConflictDetector | None = None,
        resolver: ConflictResolver | None = None,
    ) -> None:
        self.repository = ConflictRepository(session)
        self.detector = detector or ConflictDetector()
        self.resolver = resolver or ConflictResolver()

    def detect_and_persist(
        self,
        *,
        claim_id: str,
        relationships: list[EvidenceRelationship],
    ) -> list[Conflict]:
        """Detect conflicts and persist them."""

        if not claim_id:
            raise ValueError("claim_id is required.")

        detected_conflicts = self.detector.detect(
            relationships
        )

        persisted_conflicts: list[Conflict] = []

        for conflict in detected_conflicts:
            persisted = self.repository.create(
                claim_id=claim_id,
                supporting_evidence_id=(
                    conflict.supporting_evidence_id
                ),
                contradicting_evidence_id=(
                    conflict.contradicting_evidence_id
                ),
                detected_at=datetime.now(timezone.utc),
            )

            persisted_conflicts.append(persisted)

        return persisted_conflicts

    def apply_resolution(
        self,
        *,
        conflict_id: str,
        resolution: ConflictResolution,
    ) -> Conflict:
        """Persist a conflict resolution."""

        return self.repository.update_resolution(
            conflict_id=conflict_id,
            resolution_status=resolution.status.value,
            preferred_evidence_id=(
                resolution.preferred_evidence_id
            ),
            confidence=resolution.confidence,
            reasoning=resolution.reasoning,
        )