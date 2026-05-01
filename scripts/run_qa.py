from src.config.db_config import get_connection
from src.retrieval.search import search_papers
from src.rag.qa import generate_answer


def main():
    conn = get_connection()

    query = input("🔍 Ask your question: ")

    # Step 1: Retrieve relevant papers
    results = search_papers(conn, query, top_k=5)

    if not results:
        print("❌ No relevant papers found.")
        return

    # Step 2: Build context
    context = "\n\n".join([
        f"Title: {r[0]}\nAbstract: {r[1]}"
        for r in results
    ])

    # Step 3: Generate answer using DeepSeek
    #rag
    answer = generate_answer(query, context)

    print("\n🤖 Answer:\n")
    print(answer)

    conn.close()


if __name__ == "__main__":
    main()