from pydantic import BaseModel, Field

from app.models.claim import ClaimStatus


class VerificationResult(BaseModel):
    """Structured result of claim verification."""

    status: ClaimStatus

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    reasoning: str = Field(
        min_length=1,
    )