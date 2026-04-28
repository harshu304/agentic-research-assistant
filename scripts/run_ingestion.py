from src.config.db_config import get_connection
from src.ingestion.clean_data import clean_data
from src.ingestion.load_to_db import load_data

def main():
    conn = get_connection()

    data = clean_data("data/raw/papers_raw.json")

    # ✅ test only 20
    data = data[:20]

    load_data(conn, data)

    conn.close()
    print("✅ Done!")

if __name__ == "__main__":
    main()