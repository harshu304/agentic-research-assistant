def paper_exists(conn, title, source):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM papers 
        WHERE title = %s AND source = %s
        LIMIT 1;
    """, (title, source))

    exists = cursor.fetchone() is not None

    cursor.close()
    return exists