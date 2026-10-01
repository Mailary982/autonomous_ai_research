from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.researcher import ResearcherAgent
from app.schemas.planner import (
    ResearchTaskPlan,
    TaskType,
)
from app.tools.mock_fetch import MockFetchTool
from app.tools.search import SearchResult
from app.tools.search import SearchTool


class TestSearchProvider:
    """
    Deterministic search provider for the ResearcherAgent test.

    The URLs intentionally match the URLs supported by
    MockFetchTool.
    """

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title="AI Research Source One",
                url="https://mock.local/ai-agents-1",
                snippet=(
                    "Information about AI research agents."
                ),
                publisher="Test Publisher",
            ),
            SearchResult(
                title="AI Research Source Two",
                url="https://mock.local/ai-agents-2",
                snippet=(
                    "Information about evidence-grounded research."
                ),
                publisher="Test Publisher",
            ),
        ][:max_results]


def create_test_session():
    """
    Create a database session using the application's
    configured database URL.
    """

    from app.config.settings import get_settings

    settings = get_settings()

    engine = create_engine(
        settings.DATABASE_URL,
    )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return session_factory()


def main() -> None:
    print("=" * 70)
    print("RESEARCHER AGENT TEST")
    print("=" * 70)

    session = create_test_session()

    try:
        search_provider = TestSearchProvider()

        search_tool = SearchTool(
            provider=search_provider,
        )

        fetch_tool = MockFetchTool()

        agent = ResearcherAgent(
            session=session,
            search_tool=search_tool,
            fetch_tool=fetch_tool,
        )

        task = ResearchTaskPlan(
            task_id="researcher-test",
            task_type=TaskType.SOURCE_DISCOVERY,
            description=(
                "Discover sources about AI research agents."
            ),
            research_question=(
                "What are AI research agents?"
            ),
            expected_outputs=[
                "source_ids",
            ],
            dependencies=[],
            required=True,
        )

        state = {
            "research_goal": (
                "Understand AI research agents."
            ),
            "max_search_results": 2,
        }

        result = agent.execute(
            task=task,
            state=state,
        )

        print()
        print("Execution result:")
        print(
            f"  Status: {result['status']}"
        )
        print(
            f"  Sources: {result['source_count']}"
        )
        print(
            f"  Fetched: {result['fetched_count']}"
        )
        print(
            f"  Failed: {result['failed_count']}"
        )
        print(
            f"  Tool calls: {result['tool_calls']}"
        )

        print()
        print("Source IDs:")

        for source_id in result[
            "source_ids"
        ]:
            print(
                f"  - {source_id}"
            )

        assert result["status"] == "SUCCESS"

        assert result["source_count"] == 2

        assert result["fetched_count"] == 2

        assert result["failed_count"] == 0

        assert len(
            result["source_ids"]
        ) == 2

        assert result["tool_calls"] == 3

        assert all(
            isinstance(source_id, str)
            for source_id
            in result["source_ids"]
        )

        print()
        print("=" * 70)
        print("RESEARCHER AGENT TEST PASSED")
        print("=" * 70)

    finally:
        session.close()


if __name__ == "__main__":
    main()