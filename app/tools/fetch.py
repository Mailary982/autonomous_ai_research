from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class FetchedSource:
    """Structured representation of fetched source content."""

    url: str
    content: str
    content_type: str
    content_hash: str
    retrieved_at: datetime
    status_code: int


class FetchTool:
    """
    Controlled HTTP fetching tool.

    This tool is responsible for safely retrieving source content.
    External content is treated as untrusted data.
    """

    TOOL_NAME = "fetch"

    ALLOWED_SCHEMES = {"http", "https"}

    MAX_CONTENT_LENGTH = 5_000_000

    def __init__(
        self,
        timeout_seconds: int = 15,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than 0."
            )

        self.timeout_seconds = timeout_seconds

    def _validate_url(self, url: str) -> str:
        """Validate and normalize a URL before fetching."""

        if not isinstance(url, str):
            raise TypeError("url must be a string.")

        url = url.strip()

        if not url:
            raise ValueError("URL cannot be empty.")

        if len(url) > 2048:
            raise ValueError(
                "URL cannot exceed 2048 characters."
            )

        parsed = urlparse(url)

        if parsed.scheme.lower() not in self.ALLOWED_SCHEMES:
            raise ValueError(
                "Only HTTP and HTTPS URLs are allowed."
            )

        if not parsed.netloc:
            raise ValueError("URL must contain a valid host.")

        return url

    def fetch(self, url: str) -> FetchedSource:
        """
        Fetch content from a validated URL.

        Returns structured source information including a SHA-256
        content hash and retrieval timestamp.
        """

        url = self._validate_url(url)

        try:
            response = requests.get(
                url,
                timeout=self.timeout_seconds,
                headers={
                    "User-Agent": (
                        "AutonomousAIResearch/"
                        "0.1"
                    )
                },
            )

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to fetch source: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                f"Source returned HTTP {response.status_code}."
            )

        content_length = len(response.content)

        if content_length > self.MAX_CONTENT_LENGTH:
            raise RuntimeError(
                "Fetched content exceeds the maximum "
                "allowed size."
            )

        content_type = response.headers.get(
            "Content-Type",
            "application/octet-stream",
        )

        content = response.text

        content_hash = sha256(
            response.content
        ).hexdigest()

        retrieved_at = datetime.now(timezone.utc)

        return FetchedSource(
            url=url,
            content=content,
            content_type=content_type,
            content_hash=content_hash,
            retrieved_at=retrieved_at,
            status_code=response.status_code,
        )