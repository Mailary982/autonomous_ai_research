from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agents.claim_extractor import ClaimExtractor
from app.agents.evidence_extractor import EvidenceExtractor
from app.config.settings import get_settings
from app.services.claim_service import ClaimService
from app.services.evidence_service import EvidenceService
from app.services.source_service import SourceService
from app.tools.fetch import FetchTool


def main() -> None:
    settings = get_settings()

    engine = create_engine(
        settings.DATABASE_URL
    )

    fetch_tool = FetchTool()

    fetched_source = fetch_tool.fetch(
        "https://example.com"
    )

    evidence_extractor = EvidenceExtractor()

    evidence = evidence_extractor.extract(
        source_content=fetched_source.content,
        research_question=(
            "What is the purpose of example.com?"
        ),
    )

    claim_extractor = ClaimExtractor()

    claims_extraction = claim_extractor.extract(
        evidence_excerpt=evidence.excerpt,
        research_question=(
            "What is the purpose of example.com?"
        ),
    )

    with Session(engine) as session:
        source_service = SourceService(session)

        source = source_service.persist_fetched_source(
            fetched_source,
            title="Example Domain",
            publisher="IANA",
        )

        evidence_service = EvidenceService(
            session
        )

        persisted_evidence = (
            evidence_service.persist_extraction(
                source_id=source.id,
                extraction=evidence,
            )
        )

        claim_service = ClaimService(session)

        persisted_claims = (
            claim_service.persist_claims(
                extraction=claims_extraction,
                evidence_id=persisted_evidence.id,
            )
        )

        session.commit()

        print("\nSource:\n")
        print(f"ID: {source.id}")
        print(f"URI: {source.uri}")

        print("\nEvidence:\n")
        print(f"ID: {persisted_evidence.id}")
        print(
            f"Source ID: "
            f"{persisted_evidence.source_id}"
        )
        print(
            f"Excerpt: "
            f"{persisted_evidence.excerpt}"
        )

        print("\nClaims:\n")

        for index, claim in enumerate(
            persisted_claims,
            start=1,
        ):
            print(f"{index}. {claim.statement}")
            print(f"   Claim ID: {claim.id}")
            print(f"   Status: {claim.status.value}")
            print(
                "   Confidence: "
                f"{claim.confidence}"
            )


if __name__ == "__main__":
    main()