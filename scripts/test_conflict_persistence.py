from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agents.conflict_detector import EvidenceRelationship
from app.config.settings import get_settings
from app.models.claim import ClaimStatus
from app.models.evidence import Evidence
from app.models.source import Source
from app.repositories.claim_repository import ClaimRepository
from app.schemas.conflict import ConflictResolution
from app.services.conflict_service import ConflictService


def main() -> None:
    settings = get_settings()

    engine = create_engine(
        settings.DATABASE_URL,
    )

    with Session(engine) as session:
        now = datetime.now(timezone.utc)

        source = Source(
            uri="https://example.com/conflict-resolution-test",
            title="Conflict Resolution Test Source",
            publisher="Test Publisher",
            retrieved_at=now,
            source_type="web",
            content_hash=sha256(
                b"conflict-resolution-test"
            ).hexdigest(),
        )

        session.add(source)
        session.flush()

        supporting_evidence = Evidence(
            source_id=source.id,
            locator="supporting evidence",
            excerpt=(
                "The system improved performance "
                "by 20 percent."
            ),
            captured_at=now,
            evidence_quality=0.95,
        )

        contradicting_evidence = Evidence(
            source_id=source.id,
            locator="contradicting evidence",
            excerpt=(
                "The system showed no measurable "
                "performance improvement."
            ),
            captured_at=now,
            evidence_quality=0.70,
        )

        session.add_all(
            [
                supporting_evidence,
                contradicting_evidence,
            ]
        )

        session.flush()

        claim_repository = ClaimRepository(session)

        claim = claim_repository.create(
            statement=(
                "The system improves performance."
            ),
            status=ClaimStatus.UNSUPPORTED,
        )

        claim_repository.link_evidence(
            claim_id=claim.id,
            evidence_id=supporting_evidence.id,
            supports=True,
        )

        claim_repository.link_evidence(
            claim_id=claim.id,
            evidence_id=contradicting_evidence.id,
            supports=False,
        )

        session.flush()

        service = ConflictService(session)

        conflicts = service.detect_and_persist(
            claim_id=claim.id,
            relationships=[
                EvidenceRelationship(
                    evidence_id=supporting_evidence.id,
                    supports=True,
                ),
                EvidenceRelationship(
                    evidence_id=contradicting_evidence.id,
                    supports=False,
                ),
            ],
        )

        assert len(conflicts) == 1

        conflict = conflicts[0]

        print("\nConflict detected and persisted:\n")

        print(f"Conflict ID: {conflict.id}")
        print(f"Claim ID: {conflict.claim_id}")
        print(
            "Supporting evidence: "
            f"{conflict.supporting_evidence_id}"
        )
        print(
            "Contradicting evidence: "
            f"{conflict.contradicting_evidence_id}"
        )

        resolution = ConflictResolution(
            status=ClaimStatus.SUPPORTED,
            preferred_evidence_id=(
                supporting_evidence.id
            ),
            confidence=0.80,
            reasoning=(
                "The supporting evidence provides "
                "a specific quantitative finding and "
                "has a higher evidence quality score "
                "than the contradicting evidence."
            ),
        )

        resolved_conflict = service.apply_resolution(
            conflict_id=conflict.id,
            resolution=resolution,
        )

        session.commit()

        print("\nResolution persisted:\n")

        print(
            "Resolution status: "
            f"{resolved_conflict.resolution_status}"
        )

        print(
            "Preferred evidence: "
            f"{resolved_conflict.preferred_evidence_id}"
        )

        print(
            f"Confidence: {resolved_conflict.confidence}"
        )

        print(
            f"Reasoning: {resolved_conflict.reasoning}"
        )

        assert (
            resolved_conflict.resolution_status
            == "SUPPORTED"
        )

        assert (
            resolved_conflict.preferred_evidence_id
            == supporting_evidence.id
        )

        assert (
            resolved_conflict.confidence == 0.80
        )

        assert resolved_conflict.reasoning is not None

        print(
            "\nConflict resolution persistence "
            "assertion passed."
        )


if __name__ == "__main__":
    main()