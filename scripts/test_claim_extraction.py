from sqlalchemy import select

from app.agents.claim_extraction import (
    ClaimExtractionAgent,
)
from app.agents.claim_extractor import ClaimExtractor
from app.db.session import SessionLocal
from app.llm.mock_client import MockLLMClient
from app.models.claim import Claim, ClaimStatus
from app.models.claim_evidence import ClaimEvidence
from app.models.evidence import Evidence
from app.models.source import Source
from app.schemas.planner import (
    ResearchTaskPlan,
    TaskType,
)
from app.tools.mock_fetch import MockFetchTool


def main() -> None:
    print("=" * 70)
    print("CLAIM EXTRACTION AGENT TEST")
    print("=" * 70)

    db = SessionLocal()

    try:
        mock_llm = MockLLMClient()

        claim_extractor = ClaimExtractor(
            llm_client=mock_llm,
        )

        agent = ClaimExtractionAgent(
            session=db,
            claim_extractor=claim_extractor,
        )

        evidence_ids = _create_test_evidence(
            db
        )

        task = ResearchTaskPlan(
            task_id="claim-extraction-test",
            task_type=TaskType.ANALYSIS,
            description=(
                "Extract factual claims from evidence."
            ),
            research_question=(
                "What are AI research agents?"
            ),
            expected_outputs=[
                "claim_ids",
            ],
            dependencies=[
                "task-evidence",
            ],
            required=True,
        )

        state = {
            "research_goal": (
                "Understand AI research agents."
            ),
            "evidence_ids": evidence_ids,
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
            f"  Claims: {result['claim_count']}"
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
        print("Claim IDs:")

        for claim_id in result[
            "claim_ids"
        ]:
            print(
                f"  - {claim_id}"
            )

        assert result["status"] == "SUCCESS"

        assert result["claim_count"] >= 2

        assert result["failed_count"] == 0

        assert len(
            result["claim_ids"]
        ) >= 2

        assert result["tool_calls"] == 0

        assert mock_llm.call_count == 2

        for claim_id in result[
            "claim_ids"
        ]:
            claim = db.scalar(
                select(Claim).where(
                    Claim.id == claim_id
                )
            )

            assert claim is not None

            assert claim.statement

            assert (
                claim.status
                == ClaimStatus.UNSUPPORTED
            )

            assert (
                claim.confidence is None
            )

            links = list(
                db.scalars(
                    select(ClaimEvidence).where(
                        ClaimEvidence.claim_id
                        == claim_id
                    )
                ).all()
            )

            assert len(links) == 1

            assert (
                links[0].evidence_id
                in evidence_ids
            )

            assert (
                links[0].supports is True
            )

        print()
        print("Persistence checks:")
        print(
            "  Claims persisted: PASS"
        )
        print(
            "  Claims initially UNSUPPORTED: PASS"
        )
        print(
            "  Claim → Evidence links: PASS"
        )
        print(
            "  Evidence provenance preserved: PASS"
        )
        print(
            "  Mock LLM used: PASS"
        )

        print()
        print("=" * 70)
        print(
            "CLAIM EXTRACTION AGENT TEST PASSED"
        )
        print("=" * 70)

    finally:
        db.rollback()
        db.close()


def _create_test_evidence(
    db,
) -> list[str]:
    """
    Create deterministic source and evidence records.
    """

    mock_fetch = MockFetchTool()

    urls = [
        "https://mock.local/ai-agents-1",
        "https://mock.local/ai-agents-2",
    ]

    evidence_ids: list[str] = []

    for index, url in enumerate(
        urls,
        start=1,
    ):
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

        evidence = Evidence(
            source_id=source.id,
            locator="Test paragraph 1",
            excerpt=fetched.content,
            captured_at=fetched.retrieved_at,
            evidence_quality=0.95,
        )

        db.add(evidence)
        db.flush()

        evidence_ids.append(
            evidence.id
        )

    return evidence_ids


if __name__ == "__main__":
    main()