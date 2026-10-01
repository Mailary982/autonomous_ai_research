from pydantic import BaseModel, Field


class EvidenceExtraction(BaseModel):
    """Structured evidence extracted from a source."""

    excerpt: str = Field(
        min_length=1,
        description="Minimal source text supporting a factual finding.",
    )

    locator: str = Field(
        min_length=1,
        description=(
            "Location of the excerpt in the source, such as "
            "paragraph number, section, or heading."
        ),
    )

    evidence_quality: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Evidence quality score based on clarity, "
            "specificity, and directness of the evidence."
        ),
    )