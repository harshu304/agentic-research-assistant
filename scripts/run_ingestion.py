from src.config.db_config import get_connection
from src.ingestion.clean_data import clean_data
from src.ingestion.load_to_db import load_data


def main():
    conn = get_connection()

    # ❌ REMOVE full skip logic (important)
    # We allow pipeline to run every time

    data = clean_data("data/raw/papers_raw.json")

    # Optional batching (recommended for large data)
    data = data[:100]

    load_data(conn, data)

    conn.close()
    print("✅ Done!")


if __name__ == "__main__":
    main()