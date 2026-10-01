from app.agents.conflict_resolver import ConflictResolver


def main() -> None:
    resolver = ConflictResolver()

    claim = (
        "The system improves performance."
    )

    supporting_evidence = [
        {
            "evidence_id": "supporting-001",
            "excerpt": (
                "The system improved performance "
                "by 20 percent in the evaluated test."
            ),
            "evidence_quality": 0.95,
        }
    ]

    contradicting_evidence = [
        {
            "evidence_id": "contradicting-001",
            "excerpt": (
                "The evaluation found no measurable "
                "performance improvement."
            ),
            "evidence_quality": 0.70,
        }
    ]

    result = resolver.resolve(
        claim=claim,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
    )

    print("\nConflict resolution:\n")

    print(f"Status: {result.status}")
    print(
        "Preferred evidence: "
        f"{result.preferred_evidence_id}"
    )
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")

    print()

    assert result.status.value in {
        "SUPPORTED",
        "PARTIALLY_SUPPORTED",
        "CONFLICTED",
        "UNSUPPORTED",
        "OUTDATED",
    }

    assert 0.0 <= result.confidence <= 1.0

    assert result.reasoning.strip()

    print(
        "Conflict resolver assertion passed."
    )


if __name__ == "__main__":
    main()