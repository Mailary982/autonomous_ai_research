from app.agents.conflict_detector import (
    ConflictDetector,
    EvidenceRelationship,
)


def main() -> None:
    detector = ConflictDetector()

    relationships = [
        EvidenceRelationship(
            evidence_id="evidence-supporting-001",
            supports=True,
        ),
        EvidenceRelationship(
            evidence_id="evidence-supporting-002",
            supports=True,
        ),
        EvidenceRelationship(
            evidence_id="evidence-contradicting-001",
            supports=False,
        ),
    ]

    conflicts = detector.detect(
        relationships
    )

    print("\nDetected conflicts:\n")

    for conflict in conflicts:
        print(
            "Supporting evidence: "
            f"{conflict.supporting_evidence_id}"
        )

        print(
            "Contradicting evidence: "
            f"{conflict.contradicting_evidence_id}"
        )

        print()

    assert len(conflicts) == 2

    print(
        "Conflict detection assertion passed."
    )


if __name__ == "__main__":
    main()