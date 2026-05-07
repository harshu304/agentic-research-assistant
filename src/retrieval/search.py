from src.ingestion.embed import embed_query
from sentence_transformers import CrossEncoder
import re

# ==========================================
# Load reranker model (loads once)
# ==========================================
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def extract_year(query: str):
    """
    Extract year from user query
    Example:
    'papers from 2024'
    """
    match = re.search(r"\b(19|20)\d{2}\b", query)
    return int(match.group()) if match else None


def is_latest_query(query: str):
    """
    Detect latest/recent/new queries
    """
    return any(
        word in query.lower()
        for word in ["latest", "recent", "new"]
    )


def clean_query(query: str):
    """
    Clean query for semantic retrieval
    """
    return query.strip()


# ==========================================
# RERANKING FUNCTION
# ==========================================
def rerank_results(query, results, top_k=5):
    """
    Rerank retrieved papers using CrossEncoder
    """

    if not results:
        return results

    print("\n⚡ APPLYING RERANKING...")

    # query + abstract pairs
    pairs = [
        (query, r[1])  # r[1] = abstract
        for r in results
    ]

    # Generate rerank scores
    scores = reranker.predict(pairs)

    # Sort by reranker score
    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # Keep top_k final results
    final_results = [r[0] for r in reranked[:top_k]]

    print("\n✅ RERANKED RESULTS")

    for idx, (paper, score) in enumerate(reranked[:top_k], start=1):
        print(f"\n#{idx}")
        print(f"TITLE: {paper[0]}")
        print(f"YEAR: {paper[4]}")
        print(f"RERANK SCORE: {score:.4f}")

    return final_results


# ==========================================
# HYBRID SEARCH FUNCTION
# ==========================================
def hybrid_search(cursor, query_embedding, query, limit=20):

    cursor.execute("""
        SELECT
            title,
            abstract,
            pdf_url,
            authors,
            year,

            embedding <-> %s::vector AS vector_distance,

            ts_rank(
                search_vector,
                plainto_tsquery('english', %s)
            ) AS keyword_score

        FROM papers

        WHERE
            search_vector @@ plainto_tsquery('english', %s)

        ORDER BY
            vector_distance ASC,
            keyword_score DESC

        LIMIT %s;
    """, (
        query_embedding,
        query,
        query,
        limit
    ))

    return cursor.fetchall()


# ==========================================
# MAIN SEARCH FUNCTION
# ==========================================
def search_papers(conn, query, top_k=5):

    cursor = conn.cursor()

    # Clean query
    improved_query = clean_query(query)

    print(f"\n🔍 USER QUERY: {query}")
    print(f"🔍 IMPROVED QUERY: {improved_query}")

    # Generate query embedding
    query_embedding = embed_query(improved_query)

    print(f"✅ EMBEDDING DIM: {len(query_embedding)}")

    # ==========================================
    # HYBRID RETRIEVAL
    # ==========================================
    results = hybrid_search(
        cursor,
        query_embedding,
        improved_query,
        limit=20
    )

    print(f"\n📄 INITIAL RETRIEVED RESULTS: {len(results)}")

    for r in results[:5]:

        print(f"\nTITLE: {r[0]}")
        print(f"YEAR: {r[4]}")
        print(f"VECTOR DISTANCE: {r[5]}")
        print(f"KEYWORD SCORE: {r[6]}")

    # ==========================================
    # APPLY RERANKING
    # ==========================================
    results = rerank_results(
        improved_query,
        results,
        top_k=top_k
    )

    cursor.close()

    return results