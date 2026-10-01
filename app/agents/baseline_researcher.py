from app.agents.claim_extractor import ClaimExtractor
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.verifier import Verifier
from app.schemas.baseline import (
    BaselineClaimResult,
    BaselineResearchResult,
    BaselineSourceResult,
)
from app.tools.fetch import FetchTool
from app.tools.search import SearchTool


class BaselineResearcher:
    """
    Single-agent baseline for evidence-grounded research.

    This intentionally uses a simple sequential workflow.

    The baseline exists as a reference implementation for
    comparing a simple research pipeline against the later
    multi-agent architecture.
    """

    def __init__(
        self,
        search_tool: SearchTool | None = None,
        fetch_tool: FetchTool | None = None,
        evidence_extractor: EvidenceExtractor | None = None,
        claim_extractor: ClaimExtractor | None = None,
        verifier: Verifier | None = None,
    ) -> None:
        self.search_tool = search_tool or SearchTool()
        self.fetch_tool = fetch_tool or FetchTool()
        self.evidence_extractor = (
            evidence_extractor or EvidenceExtractor()
        )
        self.claim_extractor = (
            claim_extractor or ClaimExtractor()
        )
        self.verifier = verifier or Verifier()

    def research(
        self,
        research_question: str,
        max_sources: int = 3,
    ) -> BaselineResearchResult:
        """
        Execute the sequential single-agent baseline.

        Workflow:

        1. Search for sources.
        2. Fetch each source.
        3. Extract evidence.
        4. Extract claims from the evidence.
        5. Verify each claim against its evidence.
        6. Produce a deterministic summary.
        """

        self._validate_inputs(
            research_question=research_question,
            max_sources=max_sources,
        )

        tool_calls = 0
        sources: list[BaselineSourceResult] = []
        all_claims: list[BaselineClaimResult] = []
        evidence_count = 0

        # ---------------------------------------------------------
        # Step 1: Source discovery
        # ---------------------------------------------------------

        search_results = self.search_tool.search(
            query=research_question,
            max_results=max_sources,
        )

        tool_calls += 1

        # ---------------------------------------------------------
        # Step 2: Process each source sequentially
        # ---------------------------------------------------------

        for search_result in search_results:
            sources.append(
                BaselineSourceResult(
                    title=search_result.title,
                    url=search_result.url,
                    publisher=search_result.publisher,
                )
            )

            # -----------------------------------------------------
            # Step 2a: Fetch source
            # -----------------------------------------------------

            fetched = self.fetch_tool.fetch(
                search_result.url
            )

            tool_calls += 1

            # -----------------------------------------------------
            # Step 2b: Extract evidence
            #
            # IMPORTANT:
            #
            # EvidenceExtractor.extract() expects:
            #
            #     extract(source_content, research_question)
            #
            # Do NOT reverse these arguments.
            # -----------------------------------------------------

            evidence = self.evidence_extractor.extract(
                fetched.content,
                research_question,
            )

            evidence_count += 1

            # -----------------------------------------------------
            # Step 2c: Extract claims
            # -----------------------------------------------------

            claims = self.claim_extractor.extract(
                evidence.excerpt,
                research_question,
            )

            # -----------------------------------------------------
            # Step 2d: Verify claims
            # -----------------------------------------------------

            for claim in claims.claims:
                evidence_id = (
                    f"baseline-{evidence_count}"
                )

                verification = self.verifier.verify(
                    claim=claim.statement,
                    evidence=[
                        {
                            "evidence_id": evidence_id,
                            "excerpt": evidence.excerpt,
                            "evidence_quality": (
                                evidence.evidence_quality
                            ),
                        }
                    ],
                )

                all_claims.append(
                    BaselineClaimResult(
                        statement=claim.statement,
                        status=verification.status.value,
                        confidence=verification.confidence,
                        evidence_id=evidence_id,
                    )
                )

        # ---------------------------------------------------------
        # Step 3: Build deterministic summary
        # ---------------------------------------------------------

        summary = self._build_summary(
            sources=sources,
            claims=all_claims,
            evidence_count=evidence_count,
        )

        # ---------------------------------------------------------
        # Step 4: Return structured baseline result
        # ---------------------------------------------------------

        return BaselineResearchResult(
            research_question=research_question,
            sources=sources,
            claims=all_claims,
            summary=summary,
            source_count=len(sources),
            evidence_count=evidence_count,
            claim_count=len(all_claims),
            tool_calls=tool_calls,
        )

    @staticmethod
    def _validate_inputs(
        research_question: str,
        max_sources: int,
    ) -> None:
        """Validate baseline research inputs."""

        if not isinstance(research_question, str):
            raise TypeError(
                "research_question must be a string."
            )

        if not research_question.strip():
            raise ValueError(
                "research_question cannot be empty."
            )

        if not isinstance(max_sources, int):
            raise TypeError(
                "max_sources must be an integer."
            )

        if not 1 <= max_sources <= 5:
            raise ValueError(
                "max_sources must be between 1 and 5."
            )

    @staticmethod
    def _build_summary(
        sources: list[BaselineSourceResult],
        claims: list[BaselineClaimResult],
        evidence_count: int,
    ) -> str:
        """Build a deterministic baseline summary."""

        supported_count = sum(
            1
            for claim in claims
            if claim.status == "SUPPORTED"
        )

        conflicted_count = sum(
            1
            for claim in claims
            if claim.status == "CONFLICTED"
        )

        return (
            "Single-agent baseline research completed. "
            f"Collected {len(sources)} sources, "
            f"extracted {evidence_count} evidence items, "
            f"and produced {len(claims)} claims. "
            f"{supported_count} claims were supported and "
            f"{conflicted_count} claims were conflicted "
            "during verification."
        )