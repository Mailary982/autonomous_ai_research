from sqlalchemy.orm import Session

from app.agents.verifier import Verifier
from app.models.claim import Claim, ClaimStatus
from app.repositories.claim_repository import ClaimRepository
from app.schemas.claim import ClaimExtraction
from app.schemas.verification import VerificationResult


class ClaimService:
    """Application service for claim creation and verification."""

    def __init__(
        self,
        session: Session,
        verifier: Verifier | None = None,
    ) -> None:
        self.repository = ClaimRepository(session)
        self.verifier = verifier or Verifier()

    def persist_claims(
        self,
        *,
        extraction: ClaimExtraction,
        evidence_id: str,
    ) -> list[Claim]:
        """
        Persist extracted claims and associate each claim with
        the evidence from which it was derived.

        Newly extracted claims start as UNSUPPORTED because
        extraction alone does not constitute verification.
        """

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        persisted_claims: list[Claim] = []

        for item in extraction.claims:
            claim = self.repository.create(
                statement=item.statement,
                status=ClaimStatus.UNSUPPORTED,
                confidence=None,
            )

            self.repository.link_evidence(
                claim_id=claim.id,
                evidence_id=evidence_id,
                supports=True,
            )

            persisted_claims.append(claim)

        return persisted_claims

    def apply_verification(
        self,
        *,
        claim_id: str,
        verification: VerificationResult,
    ) -> Claim:
        """
        Apply a verification result to an existing claim.
        """

        return self.repository.update_verification(
            claim_id=claim_id,
            status=verification.status,
            confidence=verification.confidence,
        )