from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.claim import Claim, ClaimStatus
from app.models.claim_evidence import ClaimEvidence


class ClaimRepository:
    """Persistence operations for claims and claim-evidence links."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        statement: str,
        status: ClaimStatus = ClaimStatus.UNSUPPORTED,
        confidence: float | None = None,
    ) -> Claim:
        """Create and persist a new claim."""

        claim = Claim(
            statement=statement,
            status=status,
            confidence=confidence,
        )

        self.session.add(claim)
        self.session.flush()

        return claim

    def link_evidence(
        self,
        *,
        claim_id: str,
        evidence_id: str,
        supports: bool,
    ) -> ClaimEvidence:
        """Associate evidence with a claim."""

        link = ClaimEvidence(
            claim_id=claim_id,
            evidence_id=evidence_id,
            supports=supports,
        )

        self.session.add(link)
        self.session.flush()

        return link

    def get_by_id(
        self,
        claim_id: str,
    ) -> Claim | None:
        """Retrieve a claim by ID."""

        statement = select(Claim).where(
            Claim.id == claim_id
        )

        return self.session.scalar(statement)

    def get_by_evidence_id(
        self,
        evidence_id: str,
    ) -> list[Claim]:
        """Return claims associated with an evidence record."""

        statement = (
            select(Claim)
            .join(
                ClaimEvidence,
                ClaimEvidence.claim_id == Claim.id,
            )
            .where(
                ClaimEvidence.evidence_id == evidence_id
            )
        )

        return list(
            self.session.scalars(statement).all()
        )

    def update_verification(
        self,
        *,
        claim_id: str,
        status: ClaimStatus,
        confidence: float,
    ) -> Claim:
        """Update a claim with a verified status and confidence."""

        claim = self.get_by_id(claim_id)

        if claim is None:
            raise ValueError(
                f"Claim not found: {claim_id}"
            )

        claim.status = status
        claim.confidence = confidence

        self.session.flush()

        return claim