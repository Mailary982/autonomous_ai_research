from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import BaseResearchAgent
from app.schemas.planner import ResearchTaskPlan
from app.services.source_service import SourceService
from app.tools.fetch import FetchTool
from app.tools.search import SearchTool


class ResearcherAgent(BaseResearchAgent):
    """
    Discovers and fetches research sources.

    Outputs:
        source_ids
        source_contents
        tool_calls

    Source metadata is persisted in PostgreSQL.
    Fetched content is carried forward in workflow state
    until persistent document storage is introduced.
    """

    def __init__(
        self,
        session: Session,
        search_tool: SearchTool | None = None,
        fetch_tool: FetchTool | None = None,
    ) -> None:
        self.session = session

        self.search_tool = (
            search_tool
            or SearchTool()
        )

        self.fetch_tool = (
            fetch_tool
            or FetchTool()
        )

        self.source_service = SourceService(
            session
        )

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search for and ingest research sources.
        """

        if not isinstance(
            task,
            ResearchTaskPlan,
        ):
            raise TypeError(
                "task must be a ResearchTaskPlan."
            )

        if task.task_type.value != "SOURCE_DISCOVERY":
            raise ValueError(
                "ResearcherAgent can only execute "
                "SOURCE_DISCOVERY tasks."
            )

        research_question = (
            task.research_question.strip()
        )

        if not research_question:
            raise ValueError(
                "Research question cannot be empty."
            )

        max_results = self._get_max_results(
            state
        )

        search_results = self.search_tool.search(
            query=research_question,
            max_results=max_results,
        )

        source_ids: list[str] = []
        source_contents: dict[str, str] = {}

        fetched_count = 0
        failed_count = 0
        errors: list[str] = []

        seen_urls: set[str] = set()

        for result in search_results:
            if result.url in seen_urls:
                continue

            seen_urls.add(
                result.url
            )

            try:
                fetched_source = (
                    self.fetch_tool.fetch(
                        result.url
                    )
                )

                source = (
                    self.source_service.persist_fetched_source(
                        fetched_source,
                        title=result.title,
                        publisher=result.publisher,
                        source_type="web",
                    )
                )

                source_ids.append(
                    source.id
                )

                source_contents[
                    source.id
                ] = fetched_source.content

                fetched_count += 1

            except Exception as exc:
                failed_count += 1

                errors.append(
                    f"Failed to fetch "
                    f"{result.url}: {exc}"
                )

        if not source_ids:
            raise RuntimeError(
                "ResearcherAgent could not "
                "ingest any sources."
            )

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "status": "SUCCESS",
            "source_ids": source_ids,
            "source_contents": source_contents,
            "source_count": len(source_ids),
            "fetched_count": fetched_count,
            "failed_count": failed_count,
            "errors": errors,
            "tool_calls": 1 + len(seen_urls),
        }

    @staticmethod
    def _get_max_results(
        state: dict[str, Any],
    ) -> int:
        """
        Resolve bounded search result count.
        """

        value = state.get(
            "max_search_results",
            3,
        )

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "max_search_results must be an integer."
            )

        if not 1 <= value <= 10:
            raise ValueError(
                "max_search_results must be between 1 and 10."
            )

        return value