from tqdm import tqdm
from psycopg2.extras import execute_values
from src.ingestion.embed import embed_batch  

def process_batch(cursor, conn, batch):
    try:
        # Step 1: Extract abstracts
        # abstracts = [p["abstract"] for p in batch]
        abstracts = [p["embed_text"] for p in batch]
        # Step 2: Generate embeddings (BATCH)
        embeddings = embed_batch(abstracts)

        # Step 3: Prepare data
        data = []
        for paper, emb in zip(batch, embeddings):
            data.append((
                paper.get("paper_id"),
                paper.get("title"),
                paper.get("abstract"),
                paper.get("year"),
                paper.get("source"),
                paper.get("pdf_url"),
                paper.get("authors"),
                emb
            ))

        # Step 4: Bulk insert
        query = """
            INSERT INTO papers 
            (paper_id, title, abstract, year, source, pdf_url, authors, embedding)
            VALUES %s
            ON CONFLICT (title, source) DO NOTHING
            RETURNING id;
        """

        execute_values(cursor, query, data)

        # Step 5: Count inserted rows
        inserted_rows = cursor.fetchall()
        inserted_count = len(inserted_rows)
        skipped_count = len(data) - inserted_count

        conn.commit()

        return inserted_count, skipped_count

    except Exception as e:
        print(f"❌ Batch Error: {e}")
        conn.rollback()
        return 0, len(batch)

def load_data(conn, papers, batch_size=32):
    cursor = conn.cursor()

    total = 0
    inserted = 0
    skipped = 0

    batch = []

    for paper in tqdm(papers, desc="Processing papers"):
        total += 1

        # Skip invalid
        if not paper.get("abstract") or not paper.get("title"):
            continue

        batch.append(paper)

        # 🔥 Process batch
        if len(batch) >= batch_size:
            i, s = process_batch(cursor, conn, batch)
            inserted += i
            skipped += s
            batch = []

    # 🔥 Process remaining
    if batch:
        i, s = process_batch(cursor, conn, batch)
        inserted += i
        skipped += s

    cursor.close()

    print("\n📊 Summary:")
    print(f"📦 Total processed: {total}")
    print(f"✅ Inserted: {inserted}")
    print(f"⏭️ Skipped (conflict): {skipped}")
    print("🎉 Done!")