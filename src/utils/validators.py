import re

def clean_title(title):
    # remove year like (2023)
    title = re.sub(r'\(\d{4}\)', '', title)

    # remove bullets
    title = title.replace("-", " ")

    # normalize spaces
    title = re.sub(r'\s+', ' ', title)

    return title.strip().lower()


def validate_titles(conn, titles):

    cursor = conn.cursor()
    valid = []

    for t in titles:

        cleaned = clean_title(t)

        cursor.execute("""
            SELECT title FROM papers
            WHERE LOWER(title) LIKE %s
            LIMIT 1;
        """, ('%' + cleaned + '%',))

        result = cursor.fetchone()

        if result:
            valid.append(result[0])

    cursor.close()

    return valid