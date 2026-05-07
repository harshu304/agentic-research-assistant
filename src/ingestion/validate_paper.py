def is_research_paper(text):

    text = text.lower()

    keywords = [
        "abstract",
        "introduction",
        "methodology",
        "results",
        "conclusion",
        "references",
        "experiment",
        "dataset"
    ]

    matches = sum(
        keyword in text
        for keyword in keywords
    )

    print(f"\n📚 RESEARCH KEYWORD MATCHES: {matches}")

    return matches >= 3