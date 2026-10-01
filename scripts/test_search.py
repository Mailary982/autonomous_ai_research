from app.tools.search import SearchTool


def main() -> None:
    search_tool = SearchTool()

    results = search_tool.search(
        query="AI agents for enterprise research",
        max_results=5,
    )

    print("\nSearch results:\n")

    for index, result in enumerate(results, start=1):
        print(f"{index}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Publisher: {result.publisher}")
        print(f"   Snippet: {result.snippet}")
        print()


if __name__ == "__main__":
    main()