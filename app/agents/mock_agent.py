from typing import Any

from app.agents.base import BaseResearchAgent
from app.schemas.planner import ResearchTaskPlan


class MockResearchAgent(BaseResearchAgent):
    """
    Deterministic agent used for orchestration tests.

    It does not call an LLM or external tool.
    """

    def __init__(self, agent_name: str) -> None:
        if not agent_name.strip():
            raise ValueError(
                "agent_name cannot be empty."
            )

        self.agent_name = agent_name
        self.execution_count = 0

    def execute(
        self,
        task: ResearchTaskPlan,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        self.execution_count += 1

        return {
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "agent": self.agent_name,
            "status": "SUCCESS",
            "outputs": task.expected_outputs,
        }