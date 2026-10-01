from langgraph.graph import END, START, StateGraph

from app.graph.nodes import WorkflowNodes
from app.graph.router import WorkflowRouter
from app.graph.state import ResearchState


class ResearchWorkflow:
    """
    LangGraph implementation of the initial research workflow.

    Current version:

        START
          ↓
        plan
          ↓
        schedule
          ↓
        execute_tasks
          ↓
        schedule
          ↓
        ...
          ↓
        finalize
          ↓
        END

    The task executor is currently deterministic.
    Real specialist agents will be connected later.
    """

    def __init__(
        self,
        nodes: WorkflowNodes | None = None,
        router: WorkflowRouter | None = None,
    ) -> None:
        self.nodes = (
            nodes
            or WorkflowNodes()
        )

        self.router = (
            router
            or WorkflowRouter()
        )

    def build(self):
        """
        Build and compile the LangGraph workflow.
        """

        graph = StateGraph(
            ResearchState
        )

        # -----------------------------------------------------
        # Nodes
        # -----------------------------------------------------

        graph.add_node(
            "plan",
            self.nodes.plan,
        )

        graph.add_node(
            "schedule",
            self.nodes.schedule,
        )

        graph.add_node(
            "execute_tasks",
            self.nodes.execute_tasks,
        )

        graph.add_node(
            "finalize",
            self.nodes.finalize,
        )

        # -----------------------------------------------------
        # Entry point
        # -----------------------------------------------------

        graph.add_edge(
            START,
            "plan",
        )

        # -----------------------------------------------------
        # Planning
        # -----------------------------------------------------

        graph.add_conditional_edges(
            "plan",
            self.router.route_after_plan,
            {
                "schedule": "schedule",
                "finalize": "finalize",
            },
        )

        # -----------------------------------------------------
        # Scheduling
        # -----------------------------------------------------

        graph.add_conditional_edges(
            "schedule",
            self.router.route_after_schedule,
            {
                "execute_tasks": "execute_tasks",
                "finalize": "finalize",
            },
        )

        # -----------------------------------------------------
        # Execution
        # -----------------------------------------------------

        graph.add_conditional_edges(
            "execute_tasks",
            self.router.route_after_execution,
            {
                "schedule": "schedule",
                "finalize": "finalize",
            },
        )

        # -----------------------------------------------------
        # Completion
        # -----------------------------------------------------

        graph.add_edge(
            "finalize",
            END,
        )

        return graph.compile()