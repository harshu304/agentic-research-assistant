from src.ingestion.embed import embed_query
from sentence_transformers import CrossEncoder
import re


# ==========================================
# Load reranker model
# ==========================================
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ==========================================
# EXTRACT YEAR
# ==========================================
def extract_year(query: str):

    match = re.search(
        r"\b(19|20)\d{2}\b",
        query
    )

    return int(match.group()) if match else None


# ==========================================
# DETECT LATEST QUERY
# ==========================================
def is_latest_query(query: str):

    return any(
        word in query.lower()
        for word in ["latest", "recent", "new"]
    )


# ==========================================
# CLEAN QUERY
# ==========================================
def clean_query(query: str):

    return query.strip()


# ==========================================
# RERANKING FUNCTION
# ==========================================
def rerank_results(
    query,
    results,
    top_k=5
):

    if not results:
        return results

    print("\n⚡ APPLYING RERANKING...")

    # ==========================================
    # query + abstract pairs
    # ==========================================
    pairs = [
        (
            query,
            r[1]  # abstract
        )
        for r in results
    ]

    # ==========================================
    # Generate rerank scores
    # ==========================================
    scores = reranker.predict(pairs)

    # ==========================================
    # Sort by reranker score
    # ==========================================
    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # ==========================================
    # Keep top_k
    # ==========================================
    final_results = [
        r[0]
        for r in reranked[:top_k]
    ]

    print("\n✅ FINAL RERANKED RESULTS")

    for idx, (paper, score) in enumerate(
        reranked[:top_k],
        start=1
    ):

        print(f"\n#{idx}")

        print(f"TITLE: {paper[0]}")

        print(f"YEAR: {paper[4]}")

        print(f"RERANK SCORE: {score:.4f}")

    return final_results


# ==========================================
# VECTOR SEARCH
# ==========================================
def vector_search(
    cursor,
    query_embedding,
    year=None,
    latest=False,
    limit=20
):

    # ==========================================
    # Latest papers
    # ==========================================
    if latest:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,
                embedding <-> %s::vector AS score
            FROM papers
            ORDER BY year DESC, score
            LIMIT %s;
        """, (
            query_embedding,
            limit
        ))

    # ==========================================
    # Year-aware retrieval
    # ==========================================
    elif year:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,
                embedding <-> %s::vector AS score
            FROM papers
            WHERE year BETWEEN %s AND %s
            ORDER BY score
            LIMIT %s;
        """, (
            query_embedding,
            year - 1,
            year + 1,
            limit
        ))

    # ==========================================
    # Pure vector retrieval
    # ==========================================
    else:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,
                embedding <-> %s::vector AS score
            FROM papers
            ORDER BY score
            LIMIT %s;
        """, (
            query_embedding,
            limit
        ))

    return cursor.fetchall()


# ==========================================
# BM25 SEARCH
# ==========================================
def bm25_search(
    cursor,
    query,
    year=None,
    latest=False,
    limit=20
):

    # ==========================================
    # Latest papers
    # ==========================================
    if latest:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,

                ts_rank(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS score

            FROM papers

            WHERE
                search_vector @@
                websearch_to_tsquery('english', %s)

            ORDER BY
                year DESC,
                score DESC

            LIMIT %s;
        """, (
            query,
            query,
            limit
        ))

    # ==========================================
    # Year-aware retrieval
    # ==========================================
    elif year:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,

                ts_rank(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS score

            FROM papers

            WHERE
                year BETWEEN %s AND %s

                AND search_vector @@
                websearch_to_tsquery('english', %s)

            ORDER BY score DESC

            LIMIT %s;
        """, (
            query,
            year - 1,
            year + 1,
            query,
            limit
        ))

    # ==========================================
    # Pure BM25 retrieval
    # ==========================================
    else:

        cursor.execute("""
            SELECT
                title,
                abstract,
                pdf_url,
                authors,
                year,

                ts_rank(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS score

            FROM papers

            WHERE
                search_vector @@
                websearch_to_tsquery('english', %s)

            ORDER BY score DESC

            LIMIT %s;
        """, (
            query,
            query,
            limit
        ))

    return cursor.fetchall()


# ==========================================
# MAIN SEARCH FUNCTION
# ==========================================
def search_papers(
    conn,
    query,
    top_k=5
):

    cursor = conn.cursor()

    # ==========================================
    # Clean query
    # ==========================================
    improved_query = clean_query(query)

    print(f"\n🔍 USER QUERY: {query}")

    print(
        f"🔍 IMPROVED QUERY: "
        f"{improved_query}"
    )

    # ==========================================
    # Generate query embedding
    # ==========================================
    query_embedding = embed_query(
        improved_query
    )

    print(
        f"✅ EMBEDDING DIM: "
        f"{len(query_embedding)}"
    )

    # ==========================================
    # Query analysis
    # ==========================================
    year = extract_year(query)

    latest = is_latest_query(query)

    # ==========================================
    # VECTOR SEARCH
    # ==========================================
    vector_results = vector_search(
        cursor,
        query_embedding,
        year=year,
        latest=latest,
        limit=20
    )

    print(
        f"\n📄 VECTOR RESULTS: "
        f"{len(vector_results)}"
    )

    # ==========================================
    # BM25 SEARCH
    # ==========================================
    bm25_results = bm25_search(
        cursor,
        improved_query,
        year=year,
        latest=latest,
        limit=20
    )

    print(
        f"\n📄 BM25 RESULTS: "
        f"{len(bm25_results)}"
    )

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

        title = r[0]

        if title not in unique_results:

            unique_results[title] = r

    results = list(
        unique_results.values()
    )

    print(
        f"\n📄 UNIQUE RESULTS: "
        f"{len(results)}"
    )

    # ==========================================
    # SHOW RESULTS
    # ==========================================
    for r in results[:5]:

        print("\n====================")

        print(f"TITLE: {r[0]}")

        print(f"YEAR: {r[4]}")

        print(f"SCORE: {r[5]}")

        print("====================")

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