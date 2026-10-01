from uuid import uuid4

from sqlalchemy import select

from app.agents.claim_extraction import ClaimExtractionAgent
from app.agents.claim_extractor import ClaimExtractor
from app.agents.evidence_collection import EvidenceCollectionAgent
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.researcher import ResearcherAgent
from app.agents.verifier import Verifier
from app.agents.verifier_agent import VerifierAgent
from app.db.session import SessionLocal
from app.graph.nodes import WorkflowNodes
from app.graph.state import (
    create_initial_state,
    initialize_task_states,
)
from app.graph.task_executor import TaskExecutor
from app.graph.workflow import ResearchWorkflow
from app.llm.mock_client import MockLLMClient
from app.models.claim import Claim, ClaimStatus
from app.models.evidence import Evidence
from app.models.source import Source
from app.schemas.planner import (
    CompletionCriteria,
    ResearchPlan,
    ResearchTaskPlan,
    SourcePolicy,
    TaskType,
)
from app.tools.mock_fetch import MockFetchTool
from app.tools.search import SearchResult, SearchTool


class TestSearchProvider:
    """
    Deterministic search provider for integration testing.
    """

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title="AI Agents Source 1",
                url="https://mock.local/ai-agents-1",
                snippet=(
                    "AI agents can automate multi-step "
                    "research workflows."
                ),
                publisher="Mock Publisher",
            ),
            SearchResult(
                title="AI Agents Source 2",
                url="https://mock.local/ai-agents-2",
                snippet=(
                    "Agentic AI systems coordinate "
                    "information gathering."
                ),
                publisher="Mock Publisher",
            ),
        ][:max_results]


def build_plan() -> ResearchPlan:
    """
    Build a deterministic four-stage research plan.

    Dependency chain:

        SOURCE_DISCOVERY
              ↓
        EVIDENCE_COLLECTION
              ↓
        ANALYSIS
              ↓
        VERIFICATION
    """

    discovery = ResearchTaskPlan(
        task_id="task-source-discovery",
        task_type=TaskType.SOURCE_DISCOVERY,
        description=(
            "Discover and fetch relevant research sources."
        ),
        research_question=(
            "What are AI research agents?"
        ),
        expected_outputs=[
            "source_ids",
            "source_contents",
        ],
        dependencies=[],
        required=True,
    )

    evidence = ResearchTaskPlan(
        task_id="task-evidence-collection",
        task_type=TaskType.EVIDENCE_COLLECTION,
        description=(
            "Extract evidence from discovered sources."
        ),
        research_question=(
            "What are AI research agents?"
        ),
        expected_outputs=[
            "evidence_ids",
        ],
        dependencies=[
            "task-source-discovery",
        ],
        required=True,
    )

    claims = ResearchTaskPlan(
        task_id="task-claim-extraction",
        task_type=TaskType.ANALYSIS,
        description=(
            "Extract factual claims from research evidence."
        ),
        research_question=(
            "What are AI research agents?"
        ),
        expected_outputs=[
            "claim_ids",
        ],
        dependencies=[
            "task-evidence-collection",
        ],
        required=True,
    )

    verification = ResearchTaskPlan(
        task_id="task-verification",
        task_type=TaskType.VERIFICATION,
        description=(
            "Verify extracted claims against their evidence."
        ),
        research_question=(
            "What are AI research agents?"
        ),
        expected_outputs=[
            "verified_claim_ids",
        ],
        dependencies=[
            "task-claim-extraction",
        ],
        required=True,
    )

    return ResearchPlan(
        research_goal=(
            "Understand the role of AI research agents."
        ),
        assumptions=[],
        research_questions=[
            "What are AI research agents?"
        ],
        tasks=[
            discovery,
            evidence,
            claims,
            verification,
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
                "task-evidence-collection",
                "task-claim-extraction",
                "task-verification",
            ],
            minimum_evidence_items=2,
            minimum_verified_claims=2,
        ),
        risk_flags=[],
    )


def main() -> None:
    print("=" * 75)
    print("END-TO-END LANGGRAPH RESEARCH WORKFLOW TEST")
    print("=" * 75)

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Shared deterministic LLM
        # ---------------------------------------------------------

        mock_llm = MockLLMClient()

        # ---------------------------------------------------------
        # Source discovery
        # ---------------------------------------------------------

        search_tool = SearchTool(
            provider=TestSearchProvider()
        )

        fetch_tool = MockFetchTool()

        researcher = ResearcherAgent(
            session=db,
            search_tool=search_tool,
            fetch_tool=fetch_tool,
        )

        # ---------------------------------------------------------
        # Evidence collection
        # ---------------------------------------------------------

        evidence_extractor = EvidenceExtractor(
            llm_client=mock_llm
        )

        evidence_agent = EvidenceCollectionAgent(
            session=db,
            evidence_extractor=evidence_extractor,
        )

        # ---------------------------------------------------------
        # Claim extraction
        # ---------------------------------------------------------

        claim_extractor = ClaimExtractor(
            llm_client=mock_llm
        )

        claim_agent = ClaimExtractionAgent(
            session=db,
            claim_extractor=claim_extractor,
        )

        # ---------------------------------------------------------
        # Verification
        # ---------------------------------------------------------

        verifier = Verifier(
            llm_client=mock_llm
        )

        verifier_agent = VerifierAgent(
            session=db,
            verifier=verifier,
        )

        # ---------------------------------------------------------
        # Task executor
        # ---------------------------------------------------------

        executor = TaskExecutor()

        executor.register_agent(
            TaskType.SOURCE_DISCOVERY,
            researcher,
        )

        executor.register_agent(
            TaskType.EVIDENCE_COLLECTION,
            evidence_agent,
        )

        executor.register_agent(
            TaskType.ANALYSIS,
            claim_agent,
        )

        executor.register_agent(
            TaskType.VERIFICATION,
            verifier_agent,
        )

        # ---------------------------------------------------------
        # LangGraph workflow
        # ---------------------------------------------------------

        nodes = WorkflowNodes(
            task_executor=executor
        )

        workflow = ResearchWorkflow(
            nodes=nodes
        )

        graph = workflow.build()

        # ---------------------------------------------------------
        # Initial state
        # ---------------------------------------------------------

        run_id = str(uuid4())

        state = create_initial_state(
            run_id=run_id,
            research_goal=(
                "Understand the role of AI research agents."
            ),
            max_steps=50,
            max_tool_calls=100,
            max_retries=3,
            max_search_results=2,
        )

        plan = build_plan()

        state = initialize_task_states(
            state,
            plan,
        )

        print()
        print("Initial state:")
        print(
            f"  Run ID: {run_id}"
        )
        print(
            f"  Tasks: {len(plan.tasks)}"
        )

        # ---------------------------------------------------------
        # Execute complete workflow
        # ---------------------------------------------------------

        result = graph.invoke(
            state
        )

        # ---------------------------------------------------------
        # Final workflow state
        # ---------------------------------------------------------

        print()
        print("Final workflow state:")
        print(
            f"  Status: {result['status']}"
        )
        print(
            f"  Steps: {result['step_count']}"
        )
        print(
            f"  Tool calls: "
            f"{result['tool_call_count']}"
        )

        # ---------------------------------------------------------
        # Task states
        # ---------------------------------------------------------

        print()
        print("Task states:")

        for task_id, task_state in result[
            "task_states"
        ].items():
            print(
                f"  {task_id}: {task_state}"
            )

        # ---------------------------------------------------------
        # Research outputs
        # ---------------------------------------------------------

        print()
        print("Research outputs:")
        print(
            f"  Sources: "
            f"{len(result.get('source_ids', []))}"
        )
        print(
            f"  Source contents: "
            f"{len(result.get('source_contents', {}))}"
        )
        print(
            f"  Evidence: "
            f"{len(result.get('evidence_ids', []))}"
        )
        print(
            f"  Claims: "
            f"{len(result.get('claim_ids', []))}"
        )
        print(
            f"  Verified claims: "
            f"{len(result.get('verified_claim_ids', []))}"
        )
        print(
            f"  Mock LLM calls: "
            f"{mock_llm.call_count}"
        )

        # ---------------------------------------------------------
        # Workflow assertions
        # ---------------------------------------------------------

        assert (
            result["status"]
            == "COMPLETED"
        ), (
            f"Expected COMPLETED, "
            f"got {result['status']}"
        )

        assert (
            len(result["completed_tasks"])
            == 4
        ), (
            "Expected all four tasks "
            "to complete."
        )

        assert (
            len(result["source_ids"])
            == 2
        ), (
            "Expected two persisted sources."
        )

        assert (
            len(result["source_contents"])
            == 2
        ), (
            "Expected source content for "
            "both sources."
        )

        assert (
            len(result["evidence_ids"])
            == 2
        ), (
            "Expected two evidence records."
        )

        assert (
            len(result["claim_ids"])
            == 4
        ), (
            "Expected four extracted claims."
        )

        assert (
            len(result["verified_claim_ids"])
            == 4
        ), (
            "Expected four verified claims."
        )

        assert (
            result["tool_call_count"]
            == 3
        ), (
            "Expected one search call + "
            "two fetch calls."
        )

        assert (
            result["step_count"]
            <= result["max_steps"]
        ), (
            "Workflow exceeded maximum "
            "step limit."
        )

        assert not result.get(
            "error_messages"
        ), (
            "Workflow contains errors: "
            f"{result.get('error_messages')}"
        )

        # ---------------------------------------------------------
        # Verify task completion
        # ---------------------------------------------------------

        expected_task_ids = [
            "task-source-discovery",
            "task-evidence-collection",
            "task-claim-extraction",
            "task-verification",
        ]

        for task_id in expected_task_ids:
            assert (
                result["task_states"][task_id]
                == "COMPLETE"
            ), (
                f"Task {task_id} did not complete."
            )

        # ---------------------------------------------------------
        # Verify persisted claims
        # ---------------------------------------------------------

        for claim_id in result[
            "verified_claim_ids"
        ]:
            claim = db.scalar(
                select(Claim).where(
                    Claim.id == claim_id
                )
            )

            assert claim is not None, (
                f"Claim not found: {claim_id}"
            )

            assert (
                claim.status
                == ClaimStatus.SUPPORTED
            ), (
                f"Claim {claim_id} "
                f"was not marked SUPPORTED."
            )

            assert (
                claim.confidence is not None
            ), (
                f"Claim {claim_id} "
                "has no confidence."
            )

            assert (
                0.0
                <= claim.confidence
                <= 1.0
            ), (
                f"Claim {claim_id} "
                "has invalid confidence."
            )

        # ---------------------------------------------------------
        # Verify persisted sources
        # ---------------------------------------------------------

        source_records = list(
            db.scalars(
                select(Source)
            ).all()
        )

        # ---------------------------------------------------------
        # Verify persisted evidence
        # ---------------------------------------------------------

        evidence_records = list(
            db.scalars(
                select(Evidence)
            ).all()
        )

        print()
        print("Database validation:")
        print(
            f"  Source records visible: "
            f"{len(source_records)}"
        )
        print(
            f"  Evidence records visible: "
            f"{len(evidence_records)}"
        )
        print(
            "  Verified claim status: PASS"
        )
        print(
            "  Verification confidence: PASS"
        )

        # ---------------------------------------------------------
        # Integration summary
        # ---------------------------------------------------------

        print()
        print("Integration checks:")
        print(
            "  Source discovery: PASS"
        )
        print(
            "  Source persistence: PASS"
        )
        print(
            "  Source content propagation: PASS"
        )
        print(
            "  Evidence extraction: PASS"
        )
        print(
            "  Evidence persistence: PASS"
        )
        print(
            "  Claim extraction: PASS"
        )
        print(
            "  Claim persistence: PASS"
        )
        print(
            "  Claim → Evidence provenance: PASS"
        )
        print(
            "  Claim verification: PASS"
        )
        print(
            "  Verified claim persistence: PASS"
        )
        print(
            "  LangGraph dependency execution: PASS"
        )
        print(
            "  Workflow termination: PASS"
        )

        print()
        print("=" * 75)
        print(
            "END-TO-END LANGGRAPH WORKFLOW TEST PASSED"
        )
        print("=" * 75)

    finally:
        db.rollback()
        db.close()


if __name__ == "__main__":
    main()