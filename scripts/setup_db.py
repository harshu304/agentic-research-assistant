import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "rag_db"
USER = "postgres"
PASSWORD = "Harshu304@"
HOST = "localhost"
PORT = "5432"


def create_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' created")
    else:
        print(f"⚠️ Database '{DB_NAME}' already exists")

    cursor.close()
    conn.close()


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )


def create_table(conn):
    cursor = conn.cursor()

    # Extension
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    except:
        print("⚠️ pgvector extension already exists or not installed")

    # Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id SERIAL PRIMARY KEY,
            paper_id TEXT,
            title TEXT,
            abstract TEXT,
            year INT,
            source TEXT,
            pdf_url TEXT,
            authors TEXT,
            embedding VECTOR(384)
        );
    """)

    # Unique constraint (IMPORTANT)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_title_source
        ON papers(title, source);
    """)

    conn.commit()
    cursor.close()

    print("✅ Table ready (with deduplication)")