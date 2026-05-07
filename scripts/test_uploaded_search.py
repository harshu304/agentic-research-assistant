import psycopg2

from src.retrieval.uploaded_paper_search import (
    search_uploaded_paper
)

conn = psycopg2.connect(
    host="localhost",
    database="rag_db",
    user="postgres",
    password="Harshu304@"
)

# Paste session ID from upload step
session_id = "1899506d-2165-4a37-9b73-e39d2b34cae5"

query = "What methodology is used?"

results = search_uploaded_paper(
    conn,
    session_id,
    query
)

print("\n====================")
print("TOP RETRIEVED CHUNKS")
print("====================")

for idx, chunk in enumerate(results, start=1):

    print(f"\n--- CHUNK {idx} ---\n")

    print(chunk[0][:1000])

conn.close()