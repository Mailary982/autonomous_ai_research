from app.tools.fetch import FetchTool


def main() -> None:
    fetch_tool = FetchTool()

    source = fetch_tool.fetch(
        "https://example.com"
    )

    print("\nFetched source:\n")
    print(f"URL: {source.url}")
    print(f"Status: {source.status_code}")
    print(f"Content-Type: {source.content_type}")
    print(f"Content Hash: {source.content_hash}")
    print(f"Retrieved At: {source.retrieved_at}")
    print("\nContent:\n")
    print(source.content[:1000])


if __name__ == "__main__":
    main()