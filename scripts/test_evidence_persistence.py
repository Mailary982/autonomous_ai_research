from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.agents.evidence_extractor import EvidenceExtractor
from app.config.settings import get_settings
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

    extractor = EvidenceExtractor()

    extraction = extractor.extract(
        source_content=fetched_source.content,
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

        evidence = evidence_service.persist_extraction(
            source_id=source.id,
            extraction=extraction,
        )

        session.commit()

        print("\nSource persisted:\n")
        print(f"Source ID: {source.id}")
        print(f"Source URI: {source.uri}")
        print(f"Content Hash: {source.content_hash}")

        print("\nEvidence persisted:\n")
        print(f"Evidence ID: {evidence.id}")
        print(f"Source ID: {evidence.source_id}")
        print(f"Excerpt: {evidence.excerpt}")
        print(f"Locator: {evidence.locator}")
        print(
            f"Evidence Quality: "
            f"{evidence.evidence_quality}"
        )
        print(
            f"Captured At: "
            f"{evidence.captured_at}"
        )


if __name__ == "__main__":
    main()