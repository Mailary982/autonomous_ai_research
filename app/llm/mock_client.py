import json


class MockLLMClient:
    """
    Deterministic LLM client used for tests and local development.

    This client implements the same public interface as GeminiClient:

        generate_text(prompt: str) -> str

    It does not make any network requests and does not consume
    external LLM API quota.

    The response is selected from the structure of the prompt so
    that the existing research agents can be tested independently
    of Gemini.
    """

    def __init__(self) -> None:
        self.call_count = 0

    def generate_text(self, prompt: str) -> str:
        """
        Return a deterministic JSON response appropriate for
        the requesting agent.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "prompt cannot be empty."
            )

        self.call_count += 1

        prompt_lower = prompt.lower()

        # ---------------------------------------------------------
        # Evidence extraction
        # ---------------------------------------------------------

        if (
            "evidence extraction component" in prompt_lower
            or (
                "evidence_quality" in prompt_lower
                and "source content" in prompt_lower
                and "locator" in prompt_lower
            )
        ):
            return json.dumps(
                {
                    "excerpt": (
                        "AI agents can automate multi-step research "
                        "workflows by decomposing a research objective "
                        "into smaller tasks. They can search multiple "
                        "sources, extract relevant information, and "
                        "verify findings before producing a final report."
                    ),
                    "locator": "mock-source-content",
                    "evidence_quality": 0.90,
                }
            )

        # ---------------------------------------------------------
        # Claim extraction
        # ---------------------------------------------------------

        if (
            "claim extraction component" in prompt_lower
            or (
                '"claims"' in prompt_lower
                and "evidence_relevance" in prompt_lower
            )
        ):
            return json.dumps(
                {
                    "claims": [
                        {
                            "statement": (
                                "AI agents can automate multi-step "
                                "research workflows by decomposing "
                                "a research objective into smaller tasks."
                            ),
                            "evidence_relevance": 0.95,
                        },
                        {
                            "statement": (
                                "AI agents can search multiple sources, "
                                "extract relevant information, and "
                                "verify findings before producing "
                                "a final report."
                            ),
                            "evidence_relevance": 0.90,
                        },
                    ]
                }
            )

        # ---------------------------------------------------------
        # Verification
        # ---------------------------------------------------------

        if (
            "verification" in prompt_lower
            or (
                '"status"' in prompt_lower
                and '"confidence"' in prompt_lower
                and "evidence" in prompt_lower
            )
        ):
            return json.dumps(
                {
                    "status": "SUPPORTED",
                    "confidence": 0.95,
                    "reasoning": (
                        "The supplied evidence directly supports "
                        "the claim."
                    ),
                }
            )

        # ---------------------------------------------------------
        # Conflict resolution
        # ---------------------------------------------------------

        if (
            "conflict resolution" in prompt_lower
            or "conflicting evidence" in prompt_lower
            or "contradicting evidence" in prompt_lower
        ):
            return json.dumps(
                {
                    "status": "SUPPORTED",
                    "preferred_evidence_id": (
                        "mock-supporting-evidence"
                    ),
                    "confidence": 0.80,
                    "reasoning": (
                        "The supporting evidence is more specific "
                        "and directly relevant to the claim."
                    ),
                }
            )

        # ---------------------------------------------------------
        # Unknown prompt
        # ---------------------------------------------------------

        raise ValueError(
            "MockLLMClient does not recognize the supplied prompt."
        )