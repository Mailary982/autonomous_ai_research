from sqlalchemy import select

from app.agents.evidence_collection import (
    EvidenceCollectionAgent,
)
from app.db.session import SessionLocal
from app.llm.mock_client import MockLLMClient
from app.models.evidence import Evidence
from app.models.source import Source
from app.agents.evidence_extractor import (
    EvidenceExtractor,
)
from app.schemas.planner import (
    ResearchTaskPlan,
    TaskType,
)
from app.tools.mock_fetch import MockFetchTool


def main() -> None:
    print("=" * 70)
    print("EVIDENCE COLLECTION AGENT TEST")
    print("=" * 70)

    db = SessionLocal()

    try:
        mock_llm = MockLLMClient()

        evidence_extractor = EvidenceExtractor(
            llm_client=mock_llm,
        )

        agent = EvidenceCollectionAgent(
            session=db,
            evidence_extractor=evidence_extractor,
            fetch_tool=MockFetchTool(),
        )

        source_ids = _create_test_sources(
            db
        )

        task = ResearchTaskPlan(
            task_id="evidence-test",
            task_type=TaskType.EVIDENCE_COLLECTION,
            description=(
                "Collect evidence from discovered sources."
            ),
            research_question=(
                "What are AI research agents?"
            ),
            expected_outputs=[
                "evidence_ids",
            ],
            dependencies=[
                "task-source-discovery",
            ],
            required=True,
        )

        state = {
            "research_goal": (
                "Understand AI research agents."
            ),
            "source_ids": source_ids,
        }

        result = agent.execute(
            task=task,
            state=state,
        )

        print()
        print("Execution result:")
        print(
            f"  Status: {result['status']}"
        )
        print(
            f"  Evidence: {result['evidence_count']}"
        )
        print(
            f"  Failed: {result['failed_count']}"
        )
        print(
            f"  Tool calls: {result['tool_calls']}"
        )
        print(
            f"  LLM calls: {mock_llm.call_count}"
        )

        print()
        print("Evidence IDs:")

        for evidence_id in result[
            "evidence_ids"
        ]:
            print(
                f"  - {evidence_id}"
            )

        assert result["status"] == "SUCCESS"

        assert result["evidence_count"] == 2

        assert result["failed_count"] == 0

        assert len(
            result["evidence_ids"]
        ) == 2

        assert result["tool_calls"] == 2

        assert mock_llm.call_count == 2

        for evidence_id in result[
            "evidence_ids"
        ]:
            evidence = db.scalar(
                select(Evidence).where(
                    Evidence.id == evidence_id
                )
            )

            assert evidence is not None

            assert (
                evidence.source_id
                in source_ids
            )

            assert evidence.excerpt

            assert evidence.locator

            assert (
                evidence.evidence_quality
                is not None
            )

            assert (
                0.0
                <= evidence.evidence_quality
                <= 1.0
            )

        print()
        print("Persistence checks:")
        print(
            "  Evidence records persisted: PASS"
        )
        print(
            "  Source provenance preserved: PASS"
        )
        print(
            "  Evidence quality validated: PASS"
        )
        print(
            "  Mock LLM used: PASS"
        )

        print()
        print("=" * 70)
        print(
            "EVIDENCE COLLECTION AGENT TEST PASSED"
        )
        print("=" * 70)

    finally:
        db.rollback()
        db.close()


def _create_test_sources(
    db,
) -> list[str]:
    """
    Create two deterministic Source records.

    The URLs match MockFetchTool.
    """

    mock_fetch = MockFetchTool()

    urls = [
        "https://mock.local/ai-agents-1",
        "https://mock.local/ai-agents-2",
    ]

    source_ids: list[str] = []

    for index, url in enumerate(urls, start=1):
        fetched = mock_fetch.fetch(url)

        source = Source(
            uri=fetched.url,
            title=f"Test AI Source {index}",
            publisher="Test Publisher",
            published_at=None,
            retrieved_at=fetched.retrieved_at,
            source_type="web",
            content_hash=fetched.content_hash,
            authority_metadata=None,
        )

        db.add(source)
        db.flush()

        source_ids.append(
            source.id
        )

    return source_ids


if __name__ == "__main__":
    main()