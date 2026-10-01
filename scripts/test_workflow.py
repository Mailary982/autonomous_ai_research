from app.agents.mock_agent import MockResearchAgent
from app.agents.researcher import ResearcherAgent
from app.db.session import SessionLocal
from app.graph.nodes import WorkflowNodes
from app.graph.state_factory import (
    create_initial_state,
    initialize_task_states,
)
from app.graph.task_executor import TaskExecutor
from app.graph.workflow import ResearchWorkflow
from app.schemas.planner import (
    CompletionCriteria,
    ResearchPlan,
    ResearchTaskPlan,
    SourcePolicy,
    TaskType,
)
from app.tools.mock_fetch import MockFetchTool
from app.tools.search import SearchResult
from app.tools.search import SearchTool


class TestSearchProvider:
    """
    Deterministic search provider for the integration test.

    The URLs match MockFetchTool exactly.
    """

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        results = [
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
        ]

        return results[:max_results]


def build_test_plan() -> ResearchPlan:
    """
    Build a small plan containing one real research task
    followed by mock downstream tasks.

    This lets us verify that the real ResearcherAgent
    integrates correctly with LangGraph.
    """

    return ResearchPlan(
        research_goal=(
            "Understand how AI research agents "
            "support structured research."
        ),
        assumptions=[],
        research_questions=[
            "What are AI research agents?"
        ],
        tasks=[
            ResearchTaskPlan(
                task_id="task-source-discovery",
                task_type=TaskType.SOURCE_DISCOVERY,
                description=(
                    "Discover relevant sources."
                ),
                research_question=(
                    "What are AI research agents?"
                ),
                expected_outputs=[
                    "source_ids"
                ],
                dependencies=[],
                required=True,
            ),
            ResearchTaskPlan(
                task_id="task-evidence",
                task_type=TaskType.EVIDENCE_COLLECTION,
                description=(
                    "Collect evidence from discovered sources."
                ),
                research_question=(
                    "What are AI research agents?"
                ),
                expected_outputs=[
                    "evidence_ids"
                ],
                dependencies=[
                    "task-source-discovery"
                ],
                required=True,
            ),
            ResearchTaskPlan(
                task_id="task-analysis",
                task_type=TaskType.ANALYSIS,
                description=(
                    "Analyze collected evidence."
                ),
                research_question=(
                    "What are AI research agents?"
                ),
                expected_outputs=[
                    "claim_ids"
                ],
                dependencies=[
                    "task-evidence"
                ],
                required=True,
            ),
        ],
        source_policy=SourcePolicy(
            allowed_source_types=["web"],
            minimum_sources=2,
            require_independent_sources=True,
            allow_duplicate_sources=False,
        ),
        completion_criteria=CompletionCriteria(
            required_task_ids=[
                "task-source-discovery",
                "task-evidence",
                "task-analysis",
            ],
            minimum_evidence_items=2,
            minimum_verified_claims=1,
        ),
        risk_flags=[],
    )


def main() -> None:
    print("=" * 70)
    print("LANGGRAPH + REAL RESEARCHER INTEGRATION TEST")
    print("=" * 70)

    db = SessionLocal()

    try:
        plan = build_test_plan()

        state = create_initial_state(
            run_id="researcher-integration-test",
            research_goal=plan.research_goal,
            max_steps=20,
            max_tool_calls=20,
            max_retries=3,
        )

        state = initialize_task_states(
            state=state,
            plan=plan,
        )

        task_executor = TaskExecutor()

        researcher_agent = ResearcherAgent(
            session=db,
            search_tool=SearchTool(
                provider=TestSearchProvider()
            ),
            fetch_tool=MockFetchTool(),
        )

        evidence_agent = MockResearchAgent(
            agent_name="evidence-collector"
        )

        analysis_agent = MockResearchAgent(
            agent_name="analyst"
        )

        task_executor.register_agent(
            TaskType.SOURCE_DISCOVERY,
            researcher_agent,
        )

        task_executor.register_agent(
            TaskType.EVIDENCE_COLLECTION,
            evidence_agent,
        )

        task_executor.register_agent(
            TaskType.ANALYSIS,
            analysis_agent,
        )

        nodes = WorkflowNodes(
            task_executor=task_executor,
        )

        workflow = ResearchWorkflow(
            nodes=nodes,
        )

        graph = workflow.build()

        final_state = graph.invoke(state)

        print()
        print("Final workflow status:")
        print(
            f"  {final_state['status']}"
        )

        print()
        print("Final task states:")

        for task_id, task_state in (
            final_state["task_states"].items()
        ):
            print(
                f"  {task_id}: {task_state}"
            )

        print()
        print("Completed tasks:")

        for task_id in final_state[
            "completed_tasks"
        ]:
            print(
                f"  - {task_id}"
            )

        print()
        print(
            "Persisted source IDs:"
        )

        for source_id in final_state.get(
            "source_ids",
            [],
        ):
            print(
                f"  - {source_id}"
            )

        print()
        print(
            "Step count:",
            final_state["step_count"],
        )

        print(
            "Tool calls:",
            final_state["tool_call_count"],
        )

        assert (
            final_state["status"]
            == "COMPLETED"
        )

        assert len(
            final_state["completed_tasks"]
        ) == 3

        assert all(
            task_state == "COMPLETE"
            for task_state
            in final_state[
                "task_states"
            ].values()
        )

        assert len(
            final_state["source_ids"]
        ) == 2

        assert (
            researcher_agent is not None
        )

        assert (
            evidence_agent.execution_count == 1
        )

        assert (
            analysis_agent.execution_count == 1
        )

        assert (
            final_state["tool_call_count"]
            == 3
        )

        assert (
            final_state["step_count"]
            <= final_state["max_steps"]
        )

        print()
        print("Integration checks:")
        print(
            "  Real ResearcherAgent: PASS"
        )
        print(
            "  SearchTool: PASS"
        )
        print(
            "  MockFetchTool: PASS"
        )
        print(
            "  Source persistence: PASS"
        )
        print(
            "  TaskExecutor dispatch: PASS"
        )
        print(
            "  LangGraph orchestration: PASS"
        )

        print()
        print("=" * 70)
        print(
            "LANGGRAPH + REAL RESEARCHER "
            "INTEGRATION TEST PASSED"
        )
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()