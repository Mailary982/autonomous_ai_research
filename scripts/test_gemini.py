from app.llm.gemini_client import GeminiClient


def main() -> None:
    client = GeminiClient()

    response = client.generate_text(
        "Explain in two sentences what an AI research agent does."
    )

    print("\nGemini response:\n")
    print(response)


if __name__ == "__main__":
    main()