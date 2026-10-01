from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceRelationship:
    """Relationship between evidence and a claim."""

    evidence_id: str
    supports: bool


@dataclass(frozen=True)
class DetectedConflict:
    """A detected contradiction between two evidence records."""

    supporting_evidence_id: str
    contradicting_evidence_id: str


class ConflictDetector:
    """
    Deterministically detects conflicts from claim-evidence
    relationships.

    A conflict exists when at least one evidence record supports
    a claim and another evidence record contradicts it.
    """

    def detect(
        self,
        relationships: list[EvidenceRelationship],
    ) -> list[DetectedConflict]:
        """Detect supporting/contradicting evidence pairs."""

        if not isinstance(relationships, list):
            raise TypeError(
                "relationships must be a list."
            )

        supporting = [
            relationship.evidence_id
            for relationship in relationships
            if relationship.supports
        ]

        contradicting = [
            relationship.evidence_id
            for relationship in relationships
            if not relationship.supports
        ]

        conflicts: list[DetectedConflict] = []

        for supporting_id in supporting:
            for contradicting_id in contradicting:
                conflicts.append(
                    DetectedConflict(
                        supporting_evidence_id=supporting_id,
                        contradicting_evidence_id=contradicting_id,
                    )
                )

        return conflicts