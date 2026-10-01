from sqlalchemy import select

from app.agents.claim_extraction import ClaimExtractionAgent
from app.agents.claim_extractor import ClaimExtractor
from app.agents.verifier import Verifier
from app.agents.verifier_agent import VerifierAgent
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
from app.services.claim_service import ClaimService
from app.tools.mock_fetch import MockFetchTool


def main() -> None:
    print("=" * 70)
    print("VERIFIER AGENT TEST")
    print("=" * 70)

    db = SessionLocal()

    try:
        mock_llm = MockLLMClient()

        claim_extractor = ClaimExtractor(
            llm_client=mock_llm
        )

        claim_agent = ClaimExtractionAgent(
            session=db,
            claim_extractor=claim_extractor,
        )

        evidence_ids = _create_test_evidence(
            db
        )

        claim_task = ResearchTaskPlan(
            task_id="claim-extraction-test",
            task_type=TaskType.ANALYSIS,
            description="Extract claims.",
            research_question=(
                "What are AI research agents?"
            ),
            expected_outputs=[
                "claim_ids"
            ],
            dependencies=[],
            required=True,
        )

        claim_result = claim_agent.execute(
            task=claim_task,
            state={
                "evidence_ids": evidence_ids,
            },
        )

        claim_ids = claim_result[
            "claim_ids"
        ]

        print()
        print(
            f"Extracted claims: {len(claim_ids)}"
        )

        verifier = Verifier(
            llm_client=mock_llm
        )

        verifier_agent = VerifierAgent(
            session=db,
            verifier=verifier,
            claim_service=ClaimService(
                db,
                verifier=verifier,
            ),
        )

        verification_task = ResearchTaskPlan(
            task_id="verification-test",
            task_type=TaskType.VERIFICATION,
            description="Verify extracted claims.",
            research_question=(
                "What are AI research agents?"
            ),
            expected_outputs=[
                "verified_claim_ids"
            ],
            dependencies=[
                "claim-extraction-test"
            ],
            required=True,
        )

        verification_result = (
            verifier_agent.execute(
                task=verification_task,
                state={
                    "claim_ids": claim_ids,
                },
            )
        )

        print()
        print("Verification result:")
        print(
            f"  Status: "
            f"{verification_result['status']}"
        )
        print(
            f"  Verified claims: "
            f"{verification_result['verified_claim_count']}"
        )
        print(
            f"  Failed claims: "
            f"{verification_result['failed_count']}"
        )
        print(
            f"  Total Mock LLM calls: "
            f"{mock_llm.call_count}"
        )

        assert (
            verification_result["status"]
            == "SUCCESS"
        )

        assert (
            verification_result[
                "verified_claim_count"
            ]
            == len(claim_ids)
        )

        assert (
            verification_result[
                "failed_count"
            ]
            == 0
        )

        verified_claim_ids = (
            verification_result[
                "verified_claim_ids"
            ]
        )

        assert set(
            verified_claim_ids
        ) == set(claim_ids)

        for claim_id in claim_ids:
            claim = db.scalar(
                select(Claim).where(
                    Claim.id == claim_id
                )
            )

            assert claim is not None

            assert (
                claim.status
                == ClaimStatus.SUPPORTED
            )

            assert (
                claim.confidence is not None
            )

            assert (
                0.0
                <= claim.confidence
                <= 1.0
            )

            links = list(
                db.scalars(
                    select(ClaimEvidence).where(
                        ClaimEvidence.claim_id
                        == claim_id
                    )
                ).all()
            )

            assert len(links) >= 1

            assert all(
                link.supports is True
                for link in links
            )

        print()
        print("Persistence checks:")
        print(
            "  Claims verified: PASS"
        )
        print(
            "  Status updated: PASS"
        )
        print(
            "  Confidence persisted: PASS"
        )
        print(
            "  Evidence provenance preserved: PASS"
        )
        print(
            "  Verification failures: PASS"
        )

        print()
        print("=" * 70)
        print(
            "VERIFIER AGENT TEST PASSED"
        )
        print("=" * 70)

    finally:
        db.rollback()
        db.close()


def _create_test_evidence(
    db,
) -> list[str]:
    """
    Create deterministic source/evidence records.
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
            title=f"Verification Test Source {index}",
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