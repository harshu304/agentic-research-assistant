from src.ingestion.embed import embed_query
import re


def extract_year(query: str):
    """Extract year from user query"""
    match = re.search(r"\b(19|20)\d{2}\b", query)
    return int(match.group()) if match else None


def is_latest_query(query: str):
    """Check if user asked for latest papers"""
    return any(word in query.lower() for word in ["latest", "recent", "new"])


def clean_query(query: str):
    """
    Improve retrieval by adding research context
    """
    return query + " research paper machine learning AI"


def search_papers(conn, query, top_k=5):
    cursor = conn.cursor()

    # 🔥 Improve query for better retrieval
    improved_query = clean_query(query)

    # 🔥 Get embedding (E5 query format)
    query_embedding = embed_query(improved_query)

    year = extract_year(query)
    latest = is_latest_query(query)

    # ===============================
    # 🎯 CASE 1: Latest papers
    # ===============================
    if latest:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            ORDER BY year DESC
            LIMIT %s;
        """, (top_k,))

    # ===============================
    # 🎯 CASE 2: Year filter
    # ===============================
    elif year:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            WHERE year BETWEEN %s AND %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (year - 1, year + 1, query_embedding, top_k))

    # ===============================
    # 🎯 CASE 3: Default semantic search
    # ===============================
    else:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (query_embedding, top_k))

    results = cursor.fetchall()

    # ===============================
    # 🚨 FALLBACK (important)
    # ===============================
    if not results:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            ORDER BY year DESC
            LIMIT %s;
        """, (top_k,))
        results = cursor.fetchall()

    cursor.close()

    return results