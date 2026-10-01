import json

from app.llm.gemini_client import GeminiClient
from app.schemas.planner import ResearchPlan


class Planner:
    """
    AI Planner responsible for decomposing a research objective
    into a bounded, structured research plan.

    The Planner does NOT execute tasks.

    It only determines:

    - what needs to be researched
    - which tasks are required
    - task dependencies
    - expected outputs
    - source policy
    - completion criteria
    - research risks
    """

    def __init__(
        self,
        llm_client: GeminiClient | None = None,
    ) -> None:
        self.llm_client = (
            llm_client or GeminiClient()
        )

    def plan(
        self,
        research_goal: str,
    ) -> ResearchPlan:
        """
        Generate a structured research plan.
        """

        self._validate_input(
            research_goal
        )

        prompt = self._build_prompt(
            research_goal
        )

        response = self.llm_client.generate_text(
            prompt
        )

        return self._parse_response(
            response
        )

    @staticmethod
    def _validate_input(
        research_goal: str,
    ) -> None:
        """Validate the research objective."""

        if not isinstance(
            research_goal,
            str,
        ):
            raise TypeError(
                "research_goal must be a string."
            )

        if not research_goal.strip():
            raise ValueError(
                "research_goal cannot be empty."
            )

    @staticmethod
    def _build_prompt(
        research_goal: str,
    ) -> str:
        """Build the structured planner prompt."""

        return f"""
You are the planning component inside an
evidence-grounded autonomous research system.

Your responsibility is to decompose the user's
research objective into a bounded research plan.

You DO NOT execute research.

You DO NOT invent evidence.

You DO NOT answer the research question directly.

You only create a structured execution plan.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do not use Markdown code fences.
3. Create specific, independently executable tasks.
4. Give every task a unique task_id.
5. Explicitly define dependencies.
6. Do not create circular dependencies.
7. Keep the plan bounded.
8. Identify important research risks.
9. Define measurable completion criteria.
10. Define an explicit source policy.
11. Prefer the minimum number of tasks necessary.
12. Do not create unnecessary agents or tasks.

Task types:

- SOURCE_DISCOVERY
- EVIDENCE_COLLECTION
- ANALYSIS
- VERIFICATION
- CONFLICT_ANALYSIS
- SYNTHESIS

Research objective:

{research_goal}

Required JSON structure:

{{
  "research_goal": "string",
  "assumptions": [],
  "research_questions": [
    "string"
  ],
  "tasks": [
    {{
      "task_id": "task-1",
      "task_type": "SOURCE_DISCOVERY",
      "description": "string",
      "research_question": "string",
      "expected_outputs": [
        "string"
      ],
      "dependencies": [],
      "required": true
    }}
  ],
  "source_policy": {{
    "allowed_source_types": [
      "web"
    ],
    "minimum_sources": 3,
    "require_independent_sources": true,
    "allow_duplicate_sources": false
  }},
  "completion_criteria": {{
    "required_task_ids": [
      "task-1"
    ],
    "minimum_evidence_items": 1,
    "minimum_verified_claims": 1
  }},
  "risk_flags": []
}}

Research objective:

{research_goal}
""".strip()

    @staticmethod
    def _parse_response(
        response: str,
    ) -> ResearchPlan:
        """Parse and validate planner output."""

        if not isinstance(
            response,
            str,
        ):
            raise TypeError(
                "Planner response must be a string."
            )

        response = response.strip()

        if not response:
            raise ValueError(
                "Planner response cannot be empty."
            )

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Planner returned invalid JSON."
            ) from exc

        return ResearchPlan.model_validate(
            data
        )