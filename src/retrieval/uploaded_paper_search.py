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
    # SECTION-AWARE RETRIEVAL
    # ==========================================
    if preferred_sections:

        cursor.execute("""
            SELECT
                chunk_text,
                embedding <-> %s::vector AS distance,
                section
            FROM uploaded_paper_chunks
            WHERE
                session_id = %s
                AND section = ANY(%s)
            ORDER BY distance
            LIMIT 20;
        """, (
            query_embedding,
            session_id,
            preferred_sections
        ))

    # ==========================================
    # FALLBACK NORMAL RETRIEVAL
    # ==========================================
    else:

        cursor.execute("""
            SELECT
                chunk_text,
                embedding <-> %s::vector AS distance,
                section
            FROM uploaded_paper_chunks
            WHERE session_id = %s
            ORDER BY distance
            LIMIT 20;
        """, (
            query_embedding,
            session_id
        ))

    results = cursor.fetchall()

    print(f"\n📄 RETRIEVED CHUNKS: {len(results)}")

    for r in results[:5]:

        print("\n====================")
        print(f"SECTION: {r[2]}")
        print(f"DISTANCE: {r[1]}")
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