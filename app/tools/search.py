from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol


@dataclass(frozen=True)
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    publisher: str | None = None


class SearchProvider(Protocol):
    """Interface implemented by search providers."""

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        ...


class MockSearchProvider:
    """
    Deterministic search provider for development and testing.

    The provider intentionally returns known-fetchable URLs.
    It is not intended to represent a production search engine.
    """

    BASE_URLS = [
        "https://example.com",
        "https://example.com/",
        "https://example.com",
        "https://example.com/",
        "https://example.com",
    ]

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        if not query.strip():
            raise ValueError(
                "query cannot be empty."
            )

        if not isinstance(max_results, int):
            raise TypeError(
                "max_results must be an integer."
            )

        if not 1 <= max_results <= 10:
            raise ValueError(
                "max_results must be between 1 and 10."
            )

        query_hash = sha256(
            query.encode("utf-8")
        ).hexdigest()[:8]

        results: list[SearchResult] = []

        for index in range(max_results):
            results.append(
                SearchResult(
                    title=(
                        f"Development Research Result "
                        f"{index + 1}"
                    ),
                    url=self.BASE_URLS[index],
                    snippet=(
                        f"Deterministic development result "
                        f"for query: {query}"
                    ),
                    publisher="Development Search Provider",
                )
            )

        return results


class SearchTool:
    """
    Application-facing search tool.

    Validates inputs before delegating to a search provider.
    """

    def __init__(
        self,
        provider: SearchProvider | None = None,
    ) -> None:
        self.provider = (
            provider or MockSearchProvider()
        )

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Search for sources."""

        if not isinstance(query, str):
            raise TypeError(
                "query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "query cannot be empty."
            )

        if len(query) > 1000:
            raise ValueError(
                "query cannot exceed 1000 characters."
            )

        if not isinstance(max_results, int):
            raise TypeError(
                "max_results must be an integer."
            )

        if not 1 <= max_results <= 10:
            raise ValueError(
                "max_results must be between 1 and 10."
            )

        return self.provider.search(
            query=query,
            max_results=max_results,
        )