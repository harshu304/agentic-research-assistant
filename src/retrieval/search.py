from src.ingestion.embed import embed_text


def search_papers(conn, query, top_k=5):
    cursor = conn.cursor()

    query_embedding = embed_text(query)

    cursor.execute("""
        SELECT title, abstract
        FROM papers
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """, (query_embedding, top_k))

    results = cursor.fetchall()
    cursor.close()

    return results