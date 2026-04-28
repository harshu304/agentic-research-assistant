import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="rag_db",
        user="postgres",
        password="Harshu304@",   # 👈 your password
        host="localhost",
        port="5432"
    )