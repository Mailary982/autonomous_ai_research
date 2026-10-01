from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.settings import get_settings
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

    with Session(engine) as session:
        source_service = SourceService(session)

        source = source_service.persist_fetched_source(
            fetched_source,
            title="Example Domain",
            publisher="IANA",
        )

        session.commit()

        print("\nSource persisted successfully:\n")
        print(f"ID: {source.id}")
        print(f"URI: {source.uri}")
        print(f"Title: {source.title}")
        print(f"Publisher: {source.publisher}")
        print(f"Source Type: {source.source_type}")
        print(f"Content Hash: {source.content_hash}")
        print(f"Retrieved At: {source.retrieved_at}")


if __name__ == "__main__":
    main()