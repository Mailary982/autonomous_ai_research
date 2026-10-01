from pydantic import BaseModel, Field


class ClaimExtractionItem(BaseModel):
    """A factual claim derived from research evidence."""

    statement: str = Field(
        min_length=1,
        description="A concise factual statement.",
    )

    evidence_relevance: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How directly the provided evidence supports "
            "the claim."
        ),
    )


class ClaimExtraction(BaseModel):
    """Structured claims extracted from evidence."""

    claims: list[ClaimExtractionItem] = Field(
        min_length=1,
        max_length=10,
    )