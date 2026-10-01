from app.agents.baseline_researcher import BaselineResearcher
from app.agents.claim_extractor import ClaimExtractor
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.verifier import Verifier
from app.llm.mock_client import MockLLMClient
from app.tools.mock_fetch import MockFetchTool
from app.tools.search import SearchResult, SearchTool


class BaselineTestSearchProvider:
    """
    Deterministic search provider for baseline testing.

    No external search API is called.
    """

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        results = [
            SearchResult(
                title="AI Agents and Research Workflows",
                url="https://mock.local/ai-agents-1",
                snippet=(
                    "AI agents can automate multi-step "
                    "research workflows."
                ),
                publisher="Mock Research Publisher",
            ),
            SearchResult(
                title="Evidence-Grounded AI Research",
                url="https://mock.local/ai-agents-2",
                snippet=(
                    "Evidence grounding connects conclusions "
                    "to underlying sources."
                ),
                publisher="Mock Research Publisher",
            ),
            SearchResult(
                title="Structured Agentic Research",
                url="https://mock.local/ai-agents-3",
                snippet=(
                    "Agentic workflows can divide research "
                    "into specialized tasks."
                ),
                publisher="Mock Research Publisher",
            ),
        ]

        return results[:max_results]


def main() -> None:
    """
    Execute the deterministic single-agent baseline test.
    """

    # ---------------------------------------------------------
    # Shared deterministic LLM
    # ---------------------------------------------------------

    mock_llm = MockLLMClient()

    # ---------------------------------------------------------
    # Deterministic tools
    # ---------------------------------------------------------

    search_tool = SearchTool(
        provider=BaselineTestSearchProvider()
    )

    fetch_tool = MockFetchTool()

    # ---------------------------------------------------------
    # Agents using the mock LLM
    # ---------------------------------------------------------

    evidence_extractor = EvidenceExtractor(
        llm_client=mock_llm
    )

    claim_extractor = ClaimExtractor(
        llm_client=mock_llm
    )

    verifier = Verifier(
        llm_client=mock_llm
    )

    # ---------------------------------------------------------
    # Baseline researcher
    # ---------------------------------------------------------

    researcher = BaselineResearcher(
        search_tool=search_tool,
        fetch_tool=fetch_tool,
        evidence_extractor=evidence_extractor,
        claim_extractor=claim_extractor,
        verifier=verifier,
    )

    # ---------------------------------------------------------
    # Execute research
    # ---------------------------------------------------------

    result = researcher.research(
        research_question=(
            "What are the benefits of AI agents "
            "for enterprise research?"
        ),
        max_sources=2,
    )

    # ---------------------------------------------------------
    # Display result
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("SINGLE-AGENT BASELINE RESULT")
    print("=" * 70)

    print()
    print("Research question:")
    print(result.research_question)

    print()
    print("Sources:")
    for source in result.sources:
        print(f"  - {source.title}")
        print(f"    URL: {source.url}")
        print(f"    Publisher: {source.publisher}")

    print()
    print("Claims:")

    for index, claim in enumerate(
        result.claims,
        start=1,
    ):
        print(f"  {index}. {claim.statement}")
        print(f"     Status: {claim.status}")
        print(
            f"     Confidence: "
            f"{claim.confidence:.2f}"
        )
        print(
            f"     Evidence ID: "
            f"{claim.evidence_id}"
        )

    print()
    print("Summary:")
    print(result.summary)

    print()
    print("Metrics:")
    print(f"  Sources: {result.source_count}")
    print(f"  Evidence: {result.evidence_count}")
    print(f"  Claims: {result.claim_count}")
    print(f"  Tool calls: {result.tool_calls}")
    print(
        f"  Mock LLM calls: "
        f"{mock_llm.call_count}"
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert (
        result.research_question
        == "What are the benefits of AI agents "
           "for enterprise research?"
    )

    assert result.source_count == 2

    assert result.evidence_count == 2

    assert result.claim_count >= 1

    assert result.tool_calls == 3

    assert mock_llm.call_count >= 1

    assert result.summary

    valid_statuses = {
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "CONFLICTED",
        "UNSUPPORTED",
        "OUTDATED",
    }

    for claim in result.claims:
        assert claim.statement
        assert claim.status in valid_statuses
        assert 0.0 <= claim.confidence <= 1.0
        assert claim.evidence_id

    print()
    print("=" * 70)
    print("BASELINE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()