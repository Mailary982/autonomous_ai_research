from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import BaseResearchAgent
from app.models.evidence import Evidence
from app.schemas.planner import ResearchTaskPlan, TaskType
from app.services.claim_service import ClaimService


class ClaimExtractionAgent(BaseResearchAgent):
    """
    Extracts factual claims from persisted evidence.

    Responsibilities:
        1. Read evidence IDs from workflow state.
        2. Retrieve evidence from PostgreSQL.
        3. Pass evidence to ClaimExtractor.
        4. Persist extracted claims.
        5. Link claims to their source evidence.
        6. Return claim IDs.

    This agent does not verify claims.
    Verification is a separate workflow stage.
    """

    def __init__(
        self,
        session: Session,
        claim_extractor: Any,
        claim_service: ClaimService | None = None,
    ) -> None:
        self.session = session

        self.claim_extractor = claim_extractor

        self.claim_service = (
            claim_service
            or ClaimService(session)
        )

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract and persist claims from workflow evidence.
        """

        if not isinstance(
            task,
            ResearchTaskPlan,
        ):
            raise TypeError(
                "task must be a ResearchTaskPlan."
            )

        if task.task_type != TaskType.ANALYSIS:
            raise ValueError(
                "ClaimExtractionAgent can only execute "
                "ANALYSIS tasks."
            )

        research_question = (
            task.research_question.strip()
        )

        if not research_question:
            raise ValueError(
                "Research question cannot be empty."
            )

        evidence_ids = state.get(
            "evidence_ids",
            [],
        )

        if not isinstance(
            evidence_ids,
            list,
        ):
            raise TypeError(
                "evidence_ids must be a list."
            )

        if not evidence_ids:
            raise ValueError(
                "No evidence IDs are available "
                "for claim extraction."
            )

        claim_ids: list[str] = []
        failed_count = 0
        errors: list[str] = []

        for evidence_id in evidence_ids:
            try:
                evidence = self._get_evidence(
                    evidence_id
                )

                extraction = (
                    self.claim_extractor.extract(
                        evidence_excerpt=evidence.excerpt,
                        research_question=research_question,
                    )
                )

                claims = (
                    self.claim_service.persist_claims(
                        extraction=extraction,
                        evidence_id=evidence.id,
                    )
                )

                for claim in claims:
                    claim_ids.append(
                        claim.id
                    )

            except Exception as exc:
                failed_count += 1

                errors.append(
                    f"Failed to extract claims "
                    f"from evidence {evidence_id}: {exc}"
                )

        if not claim_ids:
            raise RuntimeError(
                "ClaimExtractionAgent could not "
                "extract any claims."
            )

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "status": "SUCCESS",
            "claim_ids": claim_ids,
            "claim_count": len(claim_ids),
            "failed_count": failed_count,
            "errors": errors,
            "tool_calls": 0,
        }

    def _get_evidence(
        self,
        evidence_id: str,
    ) -> Evidence:
        """
        Retrieve an evidence record from PostgreSQL.
        """

        if not isinstance(
            evidence_id,
            str,
        ):
            raise TypeError(
                "evidence_id must be a string."
            )

        evidence_id = evidence_id.strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        statement = (
            select(Evidence)
            .where(
                Evidence.id == evidence_id
            )
        )

        evidence = self.session.scalar(
            statement
        )

        if evidence is None:
            raise ValueError(
                f"Evidence not found: {evidence_id}"
            )

        return evidence