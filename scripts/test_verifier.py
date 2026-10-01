from app.agents.verifier import Verifier
from app.models.claim import ClaimStatus


def main() -> None:
    verifier = Verifier()

    claim = (
        "The domain is intended for use in "
        "documentation examples without requiring "
        "permission."
    )

    evidence = [
        {
            "excerpt": (
                "This domain is for use in "
                "documentation examples without "
                "needing permission."
            ),
            "locator": (
                "first paragraph tag in body"
            ),
            "evidence_quality": 0.95,
            "supports": True,
        }
    ]

    result = verifier.verify(
        claim=claim,
        evidence=evidence,
    )

    print("\nVerification result:\n")
    print(f"Status: {result.status.value}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")

    assert result.status in {
        ClaimStatus.SUPPORTED,
        ClaimStatus.PARTIALLY_SUPPORTED,
    }

    print("\nVerification assertion passed.")


if __name__ == "__main__":
    main()