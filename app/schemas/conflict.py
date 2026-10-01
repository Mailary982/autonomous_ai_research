from pydantic import BaseModel, Field

from app.models.claim import ClaimStatus


class ConflictResolution(BaseModel):
    """Structured result produced by the conflict resolver."""

    status: ClaimStatus = Field(
        description=(
            "Final verification status of the claim "
            "after considering conflicting evidence."
        )
    )

    preferred_evidence_id: str | None = Field(
        default=None,
        description=(
            "Evidence considered stronger or more reliable "
            "when resolving the conflict."
        ),
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence in the resolved claim status."
        ),
    )

    reasoning: str = Field(
        min_length=1,
        description=(
            "Explanation of how the conflicting evidence "
            "was evaluated."
        ),
    )