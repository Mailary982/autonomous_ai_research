from app.agents.evidence_extractor import EvidenceExtractor
from app.tools.fetch import FetchTool


def main() -> None:
    fetch_tool = FetchTool()

    fetched_source = fetch_tool.fetch(
        "https://example.com"
    )

    extractor = EvidenceExtractor()

    evidence = extractor.extract(
        source_content=fetched_source.content,
        research_question=(
            "What is the purpose of example.com?"
        ),
    )

    print("\nExtracted evidence:\n")
    print(f"Excerpt: {evidence.excerpt}")
    print(f"Locator: {evidence.locator}")
    print(
        f"Evidence Quality: "
        f"{evidence.evidence_quality}"
    )


if __name__ == "__main__":
    main()