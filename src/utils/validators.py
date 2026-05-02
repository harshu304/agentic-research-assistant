def validate_titles(conn, titles):
    cursor = conn.cursor()
    valid = []

    for t in titles:
        cursor.execute(
            "SELECT 1 FROM papers WHERE title=%s LIMIT 1;", 
            (t,)
        )
        if cursor.fetchone():
            valid.append(t)

    cursor.close()
    return valid