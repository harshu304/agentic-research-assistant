def validate_titles(conn, titles):
    cursor = conn.cursor()
    valid = []

    for t in titles:
        cursor.execute("""
            SELECT title FROM papers
            WHERE LOWER(title) LIKE %s
            LIMIT 1;
        """, ('%' + t + '%',))

        result = cursor.fetchone()
        if result:
            valid.append(result[0])

    cursor.close()
    return valid