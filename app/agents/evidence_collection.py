from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import BaseResearchAgent
from app.agents.evidence_extractor import EvidenceExtractor
from app.models.source import Source
from app.schemas.planner import ResearchTaskPlan, TaskType
from app.services.evidence_service import EvidenceService


class EvidenceCollectionAgent(BaseResearchAgent):
    """
    Extracts evidence from sources produced by ResearcherAgent.

    Workflow input:

        state["source_ids"]
        state["source_contents"]

    Workflow output:

        evidence_ids
    """

    def __init__(
        self,
        session: Session,
        evidence_extractor: EvidenceExtractor | None = None,
        evidence_service: EvidenceService | None = None,
    ) -> None:
        self.session = session

        self.evidence_extractor = (
            evidence_extractor
            or EvidenceExtractor()
        )

        self.evidence_service = (
            evidence_service
            or EvidenceService(session)
        )

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract and persist evidence from workflow sources.
        """

        if not isinstance(
            task,
            ResearchTaskPlan,
        ):
            raise TypeError(
                "task must be a ResearchTaskPlan."
            )

        if task.task_type != TaskType.EVIDENCE_COLLECTION:
            raise ValueError(
                "EvidenceCollectionAgent can only execute "
                "EVIDENCE_COLLECTION tasks."
            )

        research_question = (
            task.research_question.strip()
        )

        if not research_question:
            raise ValueError(
                "Research question cannot be empty."
            )

        source_ids = state.get(
            "source_ids",
            [],
        )

        if not isinstance(
            source_ids,
            list,
        ):
            raise TypeError(
                "source_ids must be a list."
            )

        if not source_ids:
            raise ValueError(
                "No source IDs are available "
                "for evidence collection."
            )

        source_contents = state.get(
            "source_contents",
            {},
        )

        if not isinstance(
            source_contents,
            dict,
        ):
            raise TypeError(
                "source_contents must be a dictionary."
            )

        evidence_ids: list[str] = []

        failed_count = 0

        errors: list[str] = []

        for source_id in source_ids:
            try:
                source = self._get_source(
                    source_id
                )

                content = source_contents.get(
                    source.id
                )

                if not isinstance(
                    content,
                    str,
                ):
                    raise ValueError(
                        f"Source content unavailable "
                        f"for source: {source.id}"
                    )

                content = content.strip()

                if not content:
                    raise ValueError(
                        f"Source content is empty "
                        f"for source: {source.id}"
                    )

                extraction = (
                    self.evidence_extractor.extract(
                        content,
                        research_question,
                    )
                )

                evidence = (
                    self.evidence_service.persist_extraction(
                        source_id=source.id,
                        extraction=extraction,
                    )
                )

                evidence_ids.append(
                    evidence.id
                )

            except Exception as exc:
                failed_count += 1

                errors.append(
                    f"Failed to extract evidence "
                    f"from source {source_id}: {exc}"
                )

        if not evidence_ids:
            raise RuntimeError(
                "EvidenceCollectionAgent could not "
                "extract any evidence."
            )

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "status": "SUCCESS",
            "evidence_ids": evidence_ids,
            "evidence_count": len(evidence_ids),
            "failed_count": failed_count,
            "errors": errors,
            "tool_calls": 0,
        }

    def _get_source(
        self,
        source_id: str,
    ) -> Source:
        """
        Retrieve a persisted source record.
        """

        if not isinstance(
            source_id,
            str,
        ):
            raise TypeError(
                "source_id must be a string."
            )

        source_id = source_id.strip()

        if not source_id:
            raise ValueError(
                "source_id cannot be empty."
            )

        statement = (
            select(Source)
            .where(
                Source.id == source_id
            )
        )

        source = self.session.scalar(
            statement
        )

        if source is None:
            raise ValueError(
                f"Source not found: {source_id}"
            )

        return source