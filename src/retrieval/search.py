from src.ingestion.embed import embed_text
import re


def extract_year(query):
    match = re.search(r"\b(19|20)\d{2}\b", query)
    return int(match.group()) if match else None


def search_papers(conn, query, top_k=5):
    cursor = conn.cursor()

    query_embedding = embed_text(query)

    year = extract_year(query)

    if year:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            WHERE year = %s
                       
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (year, query_embedding, top_k))
    else:
        cursor.execute("""
            SELECT title, abstract, pdf_url, authors, year
            FROM papers
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
        """, (query_embedding, top_k))

    results = cursor.fetchall()
    cursor.close()

    return results