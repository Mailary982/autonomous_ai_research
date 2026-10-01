from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source import Source


class SourceRepository:
    """Persistence operations for research sources."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_uri(
        self,
        uri: str,
    ) -> Source | None:
        """Return an existing source by URI."""

        statement = select(Source).where(
            Source.uri == uri
        )

        return self.session.scalar(statement)

    def get_by_content_hash(
        self,
        content_hash: str,
    ) -> Source | None:
        """Return an existing source by content hash."""

        statement = select(Source).where(
            Source.content_hash == content_hash
        )

        return self.session.scalar(statement)

    def create(
        self,
        *,
        uri: str,
        title: str | None,
        publisher: str | None,
        published_at: datetime | None,
        retrieved_at: datetime,
        source_type: str,
        content_hash: str | None,
        authority_metadata: str | None,
    ) -> Source:
        """Create and persist a new source."""

        source = Source(
            uri=uri,
            title=title,
            publisher=publisher,
            published_at=published_at,
            retrieved_at=retrieved_at,
            source_type=source_type,
            content_hash=content_hash,
            authority_metadata=authority_metadata,
        )

        self.session.add(source)
        self.session.flush()

        return source

    def get_or_create(
        self,
        *,
        uri: str,
        title: str | None,
        publisher: str | None,
        published_at: datetime | None,
        retrieved_at: datetime,
        source_type: str,
        content_hash: str | None,
        authority_metadata: str | None,
    ) -> Source:
        """
        Return an existing source when possible.

        If the URI does not exist, create a new source.
        """

        existing_source = self.get_by_uri(uri)

        if existing_source is not None:
            return existing_source

        return self.create(
            uri=uri,
            title=title,
            publisher=publisher,
            published_at=published_at,
            retrieved_at=retrieved_at,
            source_type=source_type,
            content_hash=content_hash,
            authority_metadata=authority_metadata,
        )