from src.ingestion.clean_data import clean_data
from src.ingestion.load_to_db import load_data
from scripts.setup_db import create_database, get_connection, create_table


def main():
    # Step 1: Create DB if not exists
    create_database()

    # Step 2: Connect
    conn = get_connection()

    # Step 3: Create table + index
    create_table(conn)

    # Step 4: Load data
    data = clean_data("data/raw/papers_raw.json")

    # Optional testing
    #data = data[:100]

    load_data(conn, data)

    conn.close()
    print("🎉 Pipeline completed!")


if __name__ == "__main__":
    main()