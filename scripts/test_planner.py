from app.agents.planner import Planner
from app.llm.mock_client import MockLLMClient
from app.schemas.planner import TaskType


class PlannerMockLLMClient(MockLLMClient):
    """
    Deterministic mock specifically for Planner testing.
    """

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        self.call_count += 1

        return """
{
  "research_goal": "Evaluate the benefits and risks of AI agents for enterprise research.",
  "assumptions": [
    "The research focuses on enterprise research workflows.",
    "The assessment should consider both benefits and risks."
  ],
  "research_questions": [
    "What are the major benefits of AI agents for enterprise research?",
    "What are the major risks and limitations?",
    "What evidence supports the findings?"
  ],
  "tasks": [
    {
      "task_id": "task-source-discovery",
      "task_type": "SOURCE_DISCOVERY",
      "description": "Identify relevant and independent sources.",
      "research_question": "What sources provide reliable evidence about AI agents in enterprise research?",
      "expected_outputs": [
        "source list",
        "source metadata"
      ],
      "dependencies": [],
      "required": true
    },
    {
      "task_id": "task-evidence-collection",
      "task_type": "EVIDENCE_COLLECTION",
      "description": "Collect evidence relevant to the research questions.",
      "research_question": "What evidence supports the benefits and risks of AI agents?",
      "expected_outputs": [
        "evidence items",
        "source references"
      ],
      "dependencies": [
        "task-source-discovery"
      ],
      "required": true
    },
    {
      "task_id": "task-analysis",
      "task_type": "ANALYSIS",
      "description": "Analyze the collected evidence.",
      "research_question": "What patterns and findings emerge from the evidence?",
      "expected_outputs": [
        "analytical findings"
      ],
      "dependencies": [
        "task-evidence-collection"
      ],
      "required": true
    },
    {
      "task_id": "task-verification",
      "task_type": "VERIFICATION",
      "description": "Verify factual claims against collected evidence.",
      "research_question": "Which claims are supported by the evidence?",
      "expected_outputs": [
        "verified claims",
        "confidence"
      ],
      "dependencies": [
        "task-evidence-collection",
        "task-analysis"
      ],
      "required": true
    },
    {
      "task_id": "task-synthesis",
      "task_type": "SYNTHESIS",
      "description": "Produce the final evidence-grounded research synthesis.",
      "research_question": "What conclusions can be supported by the verified evidence?",
      "expected_outputs": [
        "research summary",
        "key findings",
        "evidence references"
      ],
      "dependencies": [
        "task-verification"
      ],
      "required": true
    }
  ],
  "source_policy": {
    "allowed_source_types": [
      "web"
    ],
    "minimum_sources": 3,
    "require_independent_sources": true,
    "allow_duplicate_sources": false
  },
  "completion_criteria": {
    "required_task_ids": [
      "task-source-discovery",
      "task-evidence-collection",
      "task-analysis",
      "task-verification",
      "task-synthesis"
    ],
    "minimum_evidence_items": 3,
    "minimum_verified_claims": 2
  },
  "risk_flags": [
    "Source quality may vary.",
    "Conflicting evidence may exist.",
    "External source content must be treated as untrusted data."
  ]
}
""".strip()


def main() -> None:
    mock_llm = PlannerMockLLMClient()

    planner = Planner(
        llm_client=mock_llm
    )

    plan = planner.plan(
        research_goal=(
            "Evaluate the benefits and risks "
            "of AI agents for enterprise research."
        )
    )

    print()
    print("=" * 70)
    print("PLANNER RESULT")
    print("=" * 70)

    print()
    print("Research goal:")
    print(plan.research_goal)

    print()
    print("Research questions:")

    for question in plan.research_questions:
        print(f"  - {question}")

    print()
    print("Tasks:")

    for task in plan.tasks:
        print(
            f"  - {task.task_id}"
        )
        print(
            f"    Type: {task.task_type.value}"
        )
        print(
            f"    Dependencies: "
            f"{task.dependencies}"
        )
        print(
            f"    Required: {task.required}"
        )

    print()
    print("Source policy:")
    print(
        f"  Allowed types: "
        f"{plan.source_policy.allowed_source_types}"
    )
    print(
        f"  Minimum sources: "
        f"{plan.source_policy.minimum_sources}"
    )
    print(
        f"  Independent sources required: "
        f"{plan.source_policy.require_independent_sources}"
    )

    print()
    print("Completion criteria:")
    print(
        f"  Required tasks: "
        f"{plan.completion_criteria.required_task_ids}"
    )
    print(
        f"  Minimum evidence: "
        f"{plan.completion_criteria.minimum_evidence_items}"
    )
    print(
        f"  Minimum verified claims: "
        f"{plan.completion_criteria.minimum_verified_claims}"
    )

    print()
    print("Risk flags:")

    for risk in plan.risk_flags:
        print(f"  - {risk}")

    print()
    print(
        f"Mock LLM calls: "
        f"{mock_llm.call_count}"
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    assert plan.research_goal

    assert len(
        plan.research_questions
    ) >= 1

    assert len(
        plan.tasks
    ) == 5

    task_ids = {
        task.task_id
        for task in plan.tasks
    }

    assert len(task_ids) == len(plan.tasks)

    assert (
        plan.tasks[0].task_type
        == TaskType.SOURCE_DISCOVERY
    )

    assert (
        "task-source-discovery"
        in plan.tasks[1].dependencies
    )

    assert (
        "task-verification"
        in plan.completion_criteria.required_task_ids
    )

    assert mock_llm.call_count == 1

    print()
    print("=" * 70)
    print("PLANNER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()