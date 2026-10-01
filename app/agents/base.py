from abc import ABC, abstractmethod
from typing import Any

from app.schemas.planner import ResearchTaskPlan


class BaseResearchAgent(ABC):
    """
    Base interface for all specialist research agents.

    Every specialist agent receives:
    - the planned task
    - the current workflow state

    Every agent returns a structured dictionary that can
    be consumed by the orchestrator and persisted later.
    """

    @abstractmethod
    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the assigned research task.
        """
        raise NotImplementedError