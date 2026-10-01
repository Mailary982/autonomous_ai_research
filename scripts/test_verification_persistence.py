from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agents.claim_extractor import ClaimExtractor
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.verifier import Verifier
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

    evidence_extraction = evidence_extractor.extract(
        source_content=fetched_source.content,
        research_question=(
            "What is the purpose of example.com?"
        ),
    )

    claim_extractor = ClaimExtractor()

    claim_extraction = claim_extractor.extract(
        evidence_excerpt=evidence_extraction.excerpt,
        research_question=(
            "What is the purpose of example.com?"
        ),
    )

    verifier = Verifier()

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

        evidence = (
            evidence_service.persist_extraction(
                source_id=source.id,
                extraction=evidence_extraction,
            )
        )

        claim_service = ClaimService(
            session,
            verifier=verifier,
        )

        claims = claim_service.persist_claims(
            extraction=claim_extraction,
            evidence_id=evidence.id,
        )

        print("\nClaims before verification:\n")

        for claim in claims:
            print(f"Claim ID: {claim.id}")
            print(f"Statement: {claim.statement}")
            print(f"Status: {claim.status.value}")
            print(f"Confidence: {claim.confidence}")
            print()

        for claim in claims:
            verification = verifier.verify(
                claim=claim.statement,
                evidence=[
                    {
                        "excerpt": evidence.excerpt,
                        "locator": evidence.locator,
                        "evidence_quality": (
                            evidence.evidence_quality
                        ),
                        "supports": True,
                    }
                ],
            )

            updated_claim = (
                claim_service.apply_verification(
                    claim_id=claim.id,
                    verification=verification,
                )
            )

            print(
                "Verification applied:"
            )
            print(
                f"Status: "
                f"{updated_claim.status.value}"
            )
            print(
                f"Confidence: "
                f"{updated_claim.confidence}"
            )
            print(
                f"Reasoning: "
                f"{verification.reasoning}"
            )

        session.commit()

        print(
            "\nVerification persisted successfully."
        )


if __name__ == "__main__":
    main()