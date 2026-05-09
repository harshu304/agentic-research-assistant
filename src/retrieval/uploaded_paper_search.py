from src.ingestion.embed import embed_query
from sentence_transformers import CrossEncoder

from src.agentic.query_analyzer import (
    detect_relevant_sections
)

# ==========================================
# Load reranker
# ==========================================
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ==========================================
# RERANKING
# ==========================================
def rerank_chunks(query, results, top_k=5):

    if not results:
        return results

    # query + chunk pairs
    pairs = [
        (query, r[0])  # r[0] = chunk_text
        for r in results
    ]

    print("\n⚡ APPLYING RERANKING...")

    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    final_results = [
        r[0]
        for r in reranked[:top_k]
    ]

    print("\n✅ FINAL RERANKED CHUNKS")

    for idx, (chunk, score) in enumerate(
        reranked[:top_k],
        start=1
    ):

        print(f"\n--- CHUNK {idx} ---")

        print(f"SECTION: {chunk[2]}")

        print(f"RERANK SCORE: {score:.4f}")

    return final_results


# ==========================================
# SEARCH UPLOADED PAPER
# ==========================================
def search_uploaded_paper(
    conn,
    session_id,
    query,
    top_k=5
):

    cursor = conn.cursor()

    print(f"\n🔍 USER QUESTION: {query}")

    # ==========================================
    # Generate query embedding
    # ==========================================
    query_embedding = embed_query(query)

    # ==========================================
    # Detect preferred sections
    # ==========================================
    preferred_sections = detect_relevant_sections(query)

    print(f"\n🎯 PREFERRED SECTIONS: {preferred_sections}")

    # ==========================================
    # VECTOR SEARCH
    # ==========================================
    if preferred_sections:

        cursor.execute("""
            SELECT
                chunk_text,
                embedding <-> %s::vector AS score,
                section
            FROM uploaded_paper_chunks
            WHERE
                session_id = %s
                AND section = ANY(%s)
            ORDER BY score
            LIMIT 20;
        """, (
            query_embedding,
            session_id,
            preferred_sections
        ))

    else:

        cursor.execute("""
            SELECT
                chunk_text,
                embedding <-> %s::vector AS score,
                section
            FROM uploaded_paper_chunks
            WHERE session_id = %s
            ORDER BY score
            LIMIT 20;
        """, (
            query_embedding,
            session_id
        ))

    vector_results = cursor.fetchall()

    print(f"\n📄 VECTOR RESULTS: {len(vector_results)}")

    # ==========================================
    # BM25 SEARCH
    # ==========================================
    if preferred_sections:

        cursor.execute("""
            SELECT
                chunk_text,
                ts_rank(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS score,
                section
            FROM uploaded_paper_chunks
            WHERE
                session_id = %s
                AND section = ANY(%s)
                AND search_vector @@
                    websearch_to_tsquery('english', %s)
            ORDER BY score DESC
            LIMIT 20;
        """, (
            query,
            session_id,
            preferred_sections,
            query
        ))

    else:

        cursor.execute("""
            SELECT
                chunk_text,
                ts_rank(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS score,
                section
            FROM uploaded_paper_chunks
            WHERE
                session_id = %s
                AND search_vector @@
                    websearch_to_tsquery('english', %s)
            ORDER BY score DESC
            LIMIT 20;
        """, (
            query,
            session_id,
            query
        ))

    bm25_results = cursor.fetchall()

    print(f"\n📄 BM25 RESULTS: {len(bm25_results)}")

    # ==========================================
    # MERGE RESULTS
    # ==========================================
    combined_results = (
        vector_results +
        bm25_results
    )

    print(
        f"\n📄 COMBINED RESULTS: "
        f"{len(combined_results)}"
    )

    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================
    unique_results = {}

    for r in combined_results:

        chunk_text = r[0]

        if chunk_text not in unique_results:

            unique_results[chunk_text] = r

    results = list(unique_results.values())

    print(
        f"\n📄 UNIQUE RESULTS: "
        f"{len(results)}"
    )

    # ==========================================
    # SHOW RETRIEVED CHUNKS
    # ==========================================
    for r in results[:5]:

        print("\n====================")
        print(f"SECTION: {r[2]}")
        print(f"SCORE: {r[1]}")
        print("====================")

        print(r[0][:500])

    # ==========================================
    # APPLY RERANKING
    # ==========================================
    results = rerank_chunks(
        query,
        results,
        top_k=top_k
    )

    cursor.close()

    return results