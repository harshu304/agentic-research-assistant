from tqdm import tqdm
from src.ingestion.embed import embed_text


def load_data(conn, papers):
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for paper in tqdm(papers, desc="Inserting papers"):
        try:
            # Skip invalid
            if not paper.get("abstract") or not paper.get("title"):
                continue

            embedding = embed_text(paper["abstract"])

            cursor.execute("""
                INSERT INTO papers 
                (paper_id, title, abstract, year, source, pdf_url, authors, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title, source) DO NOTHING
                RETURNING id;
            """, (
                paper.get("paper_id"),
                paper.get("title"),
                paper.get("abstract"),
                paper.get("year"),
                paper.get("source"),
                paper.get("pdf_url"),
                paper.get("authors"),
                embedding
            ))

            # If inserted → RETURNING id gives value
            if cursor.fetchone():
                inserted += 1
            else:
                skipped += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

    conn.commit()
    cursor.close()

    print("\n📊 Summary:")
    print(f"✅ Inserted: {inserted}")
    print(f"⏭️ Skipped (already exists): {skipped}")
    print("🎉 Done!")