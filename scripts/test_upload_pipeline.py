import psycopg2

from src.ingestion.upload_pipeline import upload_research_paper


conn = psycopg2.connect(
    host="localhost",
    database="rag_db",
    user="postgres",
    password="Harshu304@"
)

pdf_path = "samle paper.pdf"

session_id = upload_research_paper(
    conn,
    pdf_path
)

print("\n🎯 SESSION ID:", session_id)

conn.close()