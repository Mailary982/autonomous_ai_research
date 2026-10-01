from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence import EvidenceExtraction


class EvidenceService:
    """Application service for evidence persistence."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = EvidenceRepository(session)

    def persist_extraction(
        self,
        *,
        source_id: str,
        extraction: EvidenceExtraction,
    ) -> Evidence:
        """
        Persist structured evidence extracted from a source.

        The source_id creates the provenance relationship between
        the evidence and the original source.
        """

        if not source_id:
            raise ValueError(
                "source_id cannot be empty."
            )

        evidence = self.repository.create(
            source_id=source_id,
            locator=extraction.locator,
            excerpt=extraction.excerpt,
            captured_at=datetime.now(timezone.utc),
            evidence_quality=extraction.evidence_quality,
        )

        return evidence