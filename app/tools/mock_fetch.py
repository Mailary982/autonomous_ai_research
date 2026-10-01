from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256


@dataclass(frozen=True)
class MockFetchedSource:
    """Deterministic fetched source for development tests."""

    url: str
    content: str
    content_type: str
    content_hash: str
    retrieved_at: datetime
    status_code: int


class MockFetchTool:
    """
    Deterministic fetch tool for development and testing.

    This avoids dependence on external websites while
    testing the research reasoning pipeline.
    """

    SOURCES = {
        "https://mock.local/ai-agents-1": (
            "AI agents can automate multi-step research "
            "workflows by decomposing a research objective "
            "into smaller tasks. They can search multiple "
            "sources, extract relevant information, and "
            "verify findings before producing a final report. "
            "This can reduce repetitive manual research work "
            "and improve consistency when evidence is tracked "
            "systematically."
        ),
        "https://mock.local/ai-agents-2": (
            "Agentic AI systems can coordinate information "
            "gathering across multiple sources. Evidence "
            "grounding allows generated conclusions to be "
            "linked to the underlying sources. Verification "
            "steps can identify unsupported claims and "
            "conflicting information before a report is "
            "generated."
        ),
        "https://mock.local/ai-agents-3": (
            "AI research agents are useful for structured "
            "information discovery and analysis. A research "
            "workflow can assign different tasks such as "
            "source discovery, evidence extraction, claim "
            "verification, and synthesis. Separating these "
            "responsibilities can make complex research "
            "workflows easier to evaluate."
        ),
    }

    def fetch(
        self,
        url: str,
    ) -> MockFetchedSource:
        """Return deterministic content for a known test URL."""

        if not isinstance(url, str):
            raise TypeError(
                "url must be a string."
            )

        url = url.strip()

        if not url:
            raise ValueError(
                "url cannot be empty."
            )

        if url not in self.SOURCES:
            raise ValueError(
                f"Unknown mock source: {url}"
            )

        content = self.SOURCES[url]

        content_hash = sha256(
            content.encode("utf-8")
        ).hexdigest()

        return MockFetchedSource(
            url=url,
            content=content,
            content_type="text/plain",
            content_hash=content_hash,
            retrieved_at=datetime.now(
                timezone.utc
            ),
            status_code=200,
        )