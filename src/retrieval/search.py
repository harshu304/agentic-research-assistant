from src.ingestion.embed import embed_query
from sentence_transformers import CrossEncoder
import re


# ==========================================
# LOAD RERANKER MODEL
# ==========================================
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ==========================================
# GLOBAL STOP WORDS
# ==========================================
STOP_WORDS = {

    # question words
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",

    # helping verbs
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "can",
    "could",
    "should",
    "would",
    "may",
    "might",
    "will",

    # articles
    "a",
    "an",
    "the",

    # prepositions
    "on",
    "in",
    "at",
    "to",
    "from",
    "for",
    "of",
    "with",
    "about",

    # generic research words
    "research",
    "paper",
    "papers",
    "study",
    "latest",
    "recent",
    "new",

    # fillers
    "tell",
    "explain",
    "give",
    "show"
}


# ==========================================
# SPELLING NORMALIZATION
# ==========================================
SPELLING_FIXES = {

    "reaserch": "research",
    "tranformer": "transformer",
    "reinforcemnt": "reinforcement",
    "algorithim": "algorithm",
    "machin": "machine"
}


# ==========================================
# QUERY EXPANSION MAP
# ==========================================
QUERY_EXPANSION = {

    "machine learning": [
        "deep learning",
        "transformers",
        "llm",
        "reinforcement learning",
        "neural networks"
    ],

    "llm": [
        "large language model",
        "transformer"
    ],

    "wireless": [
        "resource allocation",
        "communication systems",
        "5g",
        "6g"
    ]
}


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
        for word in [
            "latest",
            "recent",
            "new",
            "state of the art",
            "sota"
        ]
    )


# ==========================================
# CLEAN QUERY
# ==========================================
def clean_query(query: str):

    query = query.lower().strip()

    # spelling normalization
    for wrong, correct in SPELLING_FIXES.items():

        query = query.replace(
            wrong,
            correct
        )

    # remove special chars
    query = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        query
    )

    words = query.split()

    cleaned_words = [

        word

        for word in words

        if word not in STOP_WORDS
    ]

    cleaned_query = " ".join(
        cleaned_words
    )

    return cleaned_query


# ==========================================
# QUERY EXPANSION
# ==========================================
def expand_query(query: str):

    expanded_terms = [query]

    lower_query = query.lower()

    for key, values in QUERY_EXPANSION.items():

        if key in lower_query:

            expanded_terms.extend(values)

    expanded_query = " ".join(
        expanded_terms
    )

    return expanded_query


# ==========================================
# VECTOR SEARCH
# ==========================================
def vector_search(
    cursor,
    query_embedding,
    year=None,
    latest=False,
    limit=8
):

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

            WHERE year IS NOT NULL

            ORDER BY
                year DESC,
                score ASC

            LIMIT %s;
        """, (
            query_embedding,
            limit
        ))

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

            WHERE
                year BETWEEN %s AND %s

            ORDER BY score ASC

            LIMIT %s;
        """, (
            query_embedding,
            year - 1,
            year + 1,
            limit
        ))

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

            ORDER BY score ASC

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
    limit=8
):

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
                    websearch_to_tsquery(
                        'english',
                        %s
                    )
                ) AS score

            FROM papers

            WHERE
                year IS NOT NULL

                AND search_vector @@
                websearch_to_tsquery(
                    'english',
                    %s
                )

            ORDER BY
                year DESC,
                score DESC

            LIMIT %s;
        """, (
            query,
            query,
            limit
        ))

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
                    websearch_to_tsquery(
                        'english',
                        %s
                    )
                ) AS score

            FROM papers

            WHERE
                year BETWEEN %s AND %s

                AND search_vector @@
                websearch_to_tsquery(
                    'english',
                    %s
                )

            ORDER BY score DESC

            LIMIT %s;
        """, (
            query,
            year - 1,
            year + 1,
            query,
            limit
        ))

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
                    websearch_to_tsquery(
                        'english',
                        %s
                    )
                ) AS score

            FROM papers

            WHERE
                search_vector @@
                websearch_to_tsquery(
                    'english',
                    %s
                )

            ORDER BY score DESC

            LIMIT %s;
        """, (
            query,
            query,
            limit
        ))

    return cursor.fetchall()


# ==========================================
# DIVERSITY-AWARE RERANKING
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
    # QUERY + TITLE + ABSTRACT
    # ==========================================
    pairs = [

        (
            query,
            f"{r[0]} {r[1]}"
        )

        for r in results
    ]

    scores = reranker.predict(
        pairs
    )

    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # ==========================================
    # DIVERSITY FILTER
    # ==========================================
    final_results = []

    seen_topics = set()

    keywords = [

        "reinforcement learning",
        "transformer",
        "llm",
        "deep learning",
        "neural",
        "diffusion",
        "graph",
        "wireless",
        "resource allocation",
        "nlp"
    ]

    for paper, score in reranked:

        title = paper[0].lower()

        topic_keywords = set()

        for keyword in keywords:

            if keyword in title:

                topic_keywords.add(keyword)

        overlap = seen_topics.intersection(
            topic_keywords
        )

        # skip highly repetitive papers
        if len(overlap) >= 2:

            continue

        final_results.append(paper)

        seen_topics.update(topic_keywords)

        if len(final_results) >= top_k:

            break

    print("\n✅ FINAL DIVERSE RESULTS")

    for idx, paper in enumerate(
        final_results,
        start=1
    ):

        print(f"\n#{idx}")

        print(f"TITLE: {paper[0]}")

        print(f"YEAR: {paper[4]}")

    return final_results


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
    # CLEAN QUERY
    # ==========================================
    cleaned_query = clean_query(
        query
    )

    expanded_query = expand_query(
        cleaned_query
    )

    print(f"\n🔍 USER QUERY: {query}")

    print(
        f"🔍 CLEANED QUERY: "
        f"{cleaned_query}"
    )

    print(
        f"🔍 EXPANDED QUERY: "
        f"{expanded_query}"
    )

    # ==========================================
    # GENERATE EMBEDDING
    # ==========================================
    query_embedding = embed_query(
        expanded_query
    )

    print(
        f"✅ EMBEDDING DIM: "
        f"{len(query_embedding)}"
    )

    # ==========================================
    # QUERY ANALYSIS
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
        limit=8
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
        expanded_query,
        year=year,
        latest=latest,
        limit=8
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
    # SORT BY RECENCY
    # ==========================================
    results = sorted(
        results,
        key=lambda x: (
            x[4] if x[4] else 0
        ),
        reverse=True
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
        expanded_query,
        results,
        top_k=top_k
    )

    cursor.close()

    return results