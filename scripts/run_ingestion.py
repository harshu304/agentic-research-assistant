from src.ingestion.clean_data import clean_data_stream
from src.ingestion.load_to_db import load_data
from scripts.setup_db import create_database, get_connection, create_table


def main():
    # Step 1: Create DB
    create_database()

    # Step 2: Connect
    conn = get_connection()

    # Step 3: Create table + index
    create_table(conn)

    # Step 4: Stream data (NO MEMORY LOAD 🔥)
    papers = clean_data_stream("data/raw/papers_raw.json")

    # 🔥 Optional testing (safe way)
    # papers = (p for i, p in enumerate(papers) if i < 100)

    # Step 5: Load into DB (batch + embedding)
    load_data(conn, papers, batch_size=128)

    conn.close()
    print("🎉 Pipeline completed!")


if __name__ == "__main__":
    main()