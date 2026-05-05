from src.config.db_config import get_connection
from src.retrieval.search import search_papers
from src.rag.qa import generate_answer
from src.utils.validators import validate_titles
import re


def normalize_title(title: str):
    """Normalize title for better matching"""
    title = title.lower()
    title = re.sub(r"\(.*?\)", "", title)   # remove (year)
    title = re.sub(r"http\S+", "", title)   # remove links
    title = re.sub(r"[^a-z0-9\s]", "", title)  # remove special chars
    return title.strip()


def extract_titles(answer):
    """
    Extract titles robustly from LLM output
    Handles:
    - "- Title (Year)"
    - "- Title"
    - "- Title - extra text"
    """
    lines = answer.split("\n")
    titles = []

    for line in lines:
        line = line.strip()

        if line.startswith("-"):
            # remove bullet
            title = re.sub(r"^-+\s*", "", line)

            # remove year
            title = re.sub(r"\(\d{4}\)", "", title)

            # remove link if any
            title = re.sub(r"http\S+", "", title)

            # take only first part before extra description
            title = title.split(" - ")[0]

            title = title.strip()

            if title:
                titles.append(title)

    # remove duplicates
    return list(set(titles))


def main():
    conn = get_connection()

    query = input("🔍 Ask your question: ")

    # 🔥 Step 1: Retrieve papers
    results = search_papers(conn, query, top_k=5)

    if not results:
        print("❌ No relevant papers found.")
        return

    # 🔍 DEBUG: Check retrieval
    print("\n🔍 Retrieved Papers:\n")
    for r in results:
        print(f"{r[0]} ({r[4]})")

    # 🔥 Step 2: Build strong context
    context = "\n\n".join([
        f"""[PAPER]
Title: {r[0]}
Year: {r[4]}
Authors: {r[3]}
Link: {r[2]}

Abstract:
{(r[1] or '')[:300]}
"""
        for r in results
    ])

    # 🔥 Step 3: LLM answer
    answer = generate_answer(query, context)

    print("\n🤖 Answer:\n")
    print(answer)

    # 🔥 Step 4: Extract titles
    extracted_titles = extract_titles(answer)

    # Normalize before validation
    extracted_titles = [normalize_title(t) for t in extracted_titles]

    # 🔥 Step 5: Validate with DB
    valid_titles = validate_titles(conn, extracted_titles)

    # 🔥 Step 6: Output
    print("\n📚 Valid References (from DB):\n")

    if not valid_titles:
        print("⚠️ No valid references found")
        print("👉 Possible reasons:")
        print("   - LLM format mismatch")
        print("   - Weak retrieval")
        print("   - Titles slightly different")
    else:
        for t in valid_titles:
            print("-", t)

    conn.close()


if __name__ == "__main__":
    main()