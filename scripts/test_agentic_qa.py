import psycopg2

from src.agentic.agentic_pipeline import (
    agentic_qa_pipeline
)

conn = psycopg2.connect(
    host="localhost",
    database="rag_db",
    user="postgres",
    password="Harshu304@"
)

session_id = "1899506d-2165-4a37-9b73-e39d2b34cae5"

question = "What methodology is used?"

answer = agentic_qa_pipeline(
    conn,
    session_id,
    question
)

print("\n====================")
print("FINAL ANSWER")
print("====================\n")

print(answer)

conn.close()