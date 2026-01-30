from model.db import get_connection

def get_course_id_by_name(course_name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id FROM courses WHERE name = %s"
    cursor.execute(query, (course_name,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row["id"]
    return None

