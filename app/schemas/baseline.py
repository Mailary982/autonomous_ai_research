from pydantic import BaseModel, Field


class BaselineSourceResult(BaseModel):
    """Source information collected during baseline research."""

    title: str
    url: str
    publisher: str | None = None


class BaselineClaimResult(BaseModel):
    """Verified claim produced by the baseline."""

    statement: str
    status: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    evidence_id: str


class BaselineResearchResult(BaseModel):
    """Complete result produced by the single-agent baseline."""

    research_question: str

    sources: list[BaselineSourceResult]

    claims: list[BaselineClaimResult]

    summary: str

    source_count: int = Field(
        ge=0,
    )

    evidence_count: int = Field(
        ge=0,
    )

    claim_count: int = Field(
        ge=0,
    )

    tool_calls: int = Field(
        ge=0,
    )