from src.config.db_config import get_connection
from src.retrieval.search import search_papers
from src.rag.qa import generate_answer
from src.utils.validators import validate_titles
import re


def extract_titles(answer):
    """
    Extract paper titles from LLM output.
    Assumes format:
    - Title (Year)
    or
    - Title
    """
    lines = answer.split("\n")
    titles = []

    for line in lines:
        line = line.strip()

        if line.startswith("- "):
            title = line.replace("- ", "").strip()

            # Remove year if present (e.g., "Title (2020)")
            title = re.sub(r"\(\d{4}\)", "", title).strip()

            titles.append(title)

    return titles


def main():
    conn = get_connection()

    query = input("🔍 Ask your question: ")

    # Step 1: Retrieve relevant papers
    results = search_papers(conn, query, top_k=5)

    if not results:
        print("❌ No relevant papers found.")
        return

    # Step 2: Build context (IMPORTANT)
    context = "\n\n".join([
        f"""Paper:
Title: {r[0]}
Link: {r[2]}
Authors: {r[3]}
Year: {r[4]}

Abstract:
{(r[1] or '')[:400]}
"""
        for r in results
    ])

    # Step 3: Generate answer (LLM)
    answer = generate_answer(query, context)

    print("\n🤖 Answer:\n")
    print(answer)

    # Step 4: Extract titles from answer
    extracted_titles = extract_titles(answer)

    # Step 5: Validate against DB
    valid_titles = validate_titles(conn, extracted_titles)

    # Step 6: Show only valid references
    print("\n📚 Valid References (from DB):\n")

    if not valid_titles:
        print("⚠️ No valid references found (LLM hallucinated or format mismatch)")
    else:
        for t in valid_titles:
            print("-", t)

    conn.close()


if __name__ == "__main__":
    main()