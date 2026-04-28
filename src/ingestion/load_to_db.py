from tqdm import tqdm
from src.ingestion.embed import embed_text


def load_data(conn, papers):
    cursor = conn.cursor()

    for paper in tqdm(papers, desc="Inserting papers"):
        try:
            if not paper["abstract"] or not paper["title"]:
                continue

            embedding = embed_text(paper["abstract"])

            cursor.execute("""
                INSERT INTO papers 
                (paper_id, title, abstract, year, source, pdf_url, authors, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (paper_id) DO NOTHING;
            """, (
                paper["paper_id"],
                paper["title"],
                paper["abstract"],
                paper["year"],
                paper["source"],
                paper["pdf_url"],
                paper["authors"],
                embedding
            ))

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

    conn.commit()
    cursor.close()

    print("✅ Data inserted successfully!")