from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import BaseResearchAgent
from app.agents.verifier import Verifier
from app.models.claim import Claim
from app.models.claim_evidence import ClaimEvidence
from app.models.evidence import Evidence
from app.schemas.planner import ResearchTaskPlan, TaskType
from app.services.claim_service import ClaimService


class VerifierAgent(BaseResearchAgent):
    """
    Verifies persisted claims against their associated evidence.

    Workflow:

        claim_ids
            ↓
        Claim records
            ↓
        ClaimEvidence links
            ↓
        Evidence records
            ↓
        Verifier
            ↓
        VerificationResult
            ↓
        ClaimService
            ↓
        Updated Claim
    """

    def __init__(
        self,
        session: Session,
        verifier: Verifier | None = None,
        claim_service: ClaimService | None = None,
    ) -> None:
        self.session = session

        self.verifier = (
            verifier
            or Verifier()
        )

        self.claim_service = (
            claim_service
            or ClaimService(
                session,
                verifier=self.verifier,
            )
        )

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Verify all claims available in workflow state.
        """

        if not isinstance(
            task,
            ResearchTaskPlan,
        ):
            raise TypeError(
                "task must be a ResearchTaskPlan."
            )

        if task.task_type != TaskType.VERIFICATION:
            raise ValueError(
                "VerifierAgent can only execute "
                "VERIFICATION tasks."
            )

        claim_ids = state.get(
            "claim_ids",
            [],
        )

        if not isinstance(
            claim_ids,
            list,
        ):
            raise TypeError(
                "claim_ids must be a list."
            )

        if not claim_ids:
            raise ValueError(
                "No claim IDs are available "
                "for verification."
            )

        verified_claim_ids: list[str] = []
        failed_claim_ids: list[str] = []
        errors: list[str] = []

        for claim_id in claim_ids:
            try:
                claim = self._get_claim(
                    claim_id
                )

                evidence = (
                    self._get_claim_evidence(
                        claim.id
                    )
                )

                if not evidence:
                    raise ValueError(
                        f"No evidence is linked "
                        f"to claim: {claim.id}"
                    )

                evidence_payload = [
                    {
                        "evidence_id": item.id,
                        "excerpt": item.excerpt,
                        "locator": item.locator or "",
                        "evidence_quality": (
                            item.evidence_quality
                            if item.evidence_quality
                            is not None
                            else 0.0
                        ),
                        "supports": supports,
                    }
                    for item, supports in evidence
                ]

                verification = (
                    self.verifier.verify(
                        claim=claim.statement,
                        evidence=evidence_payload,
                    )
                )

                updated_claim = (
                    self.claim_service.apply_verification(
                        claim_id=claim.id,
                        verification=verification,
                    )
                )

                verified_claim_ids.append(
                    updated_claim.id
                )

            except Exception as exc:
                failed_claim_ids.append(
                    claim_id
                )

                errors.append(
                    f"Failed to verify claim "
                    f"{claim_id}: {exc}"
                )

        if not verified_claim_ids:
            raise RuntimeError(
                "VerifierAgent could not verify "
                "any claims."
            )

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "status": "SUCCESS",
            "verified_claim_ids": verified_claim_ids,
            "failed_claim_ids": failed_claim_ids,
            "verified_claim_count": len(
                verified_claim_ids
            ),
            "failed_count": len(
                failed_claim_ids
            ),
            "errors": errors,
            "tool_calls": 0,
        }

    def _get_claim(
        self,
        claim_id: str,
    ) -> Claim:
        """
        Retrieve a persisted claim.
        """

        if not isinstance(
            claim_id,
            str,
        ):
            raise TypeError(
                "claim_id must be a string."
            )

        claim_id = claim_id.strip()

        if not claim_id:
            raise ValueError(
                "claim_id cannot be empty."
            )

        statement = (
            select(Claim)
            .where(
                Claim.id == claim_id
            )
        )

        claim = self.session.scalar(
            statement
        )

        if claim is None:
            raise ValueError(
                f"Claim not found: {claim_id}"
            )

        return claim

    def _get_claim_evidence(
        self,
        claim_id: str,
    ) -> list[tuple[Evidence, bool]]:
        """
        Retrieve evidence associated with a claim.

        Returns tuples of:

            (Evidence, supports)
        """

        statement = (
            select(
                Evidence,
                ClaimEvidence.supports,
            )
            .join(
                ClaimEvidence,
                ClaimEvidence.evidence_id
                == Evidence.id,
            )
            .where(
                ClaimEvidence.claim_id
                == claim_id
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        return [
            (
                row[0],
                row[1],
            )
            for row in rows
        ]