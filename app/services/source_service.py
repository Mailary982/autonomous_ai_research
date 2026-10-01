from sqlalchemy.orm import Session

from app.models.source import Source
from app.repositories.source_repository import SourceRepository
from app.tools.fetch import FetchedSource


class SourceService:
    """Application service for source ingestion and persistence."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = SourceRepository(session)

    def persist_fetched_source(
        self,
        fetched_source: FetchedSource,
        *,
        title: str | None = None,
        publisher: str | None = None,
        source_type: str = "web",
    ) -> Source:
        """
        Persist metadata for a fetched source.

        The fetched content itself is intentionally not stored in
        the Source table. The content will later be transformed
        into evidence records.
        """

        source = self.repository.get_or_create(
            uri=fetched_source.url,
            title=title,
            publisher=publisher,
            published_at=None,
            retrieved_at=fetched_source.retrieved_at,
            source_type=source_type,
            content_hash=fetched_source.content_hash,
            authority_metadata=None,
        )

        return source