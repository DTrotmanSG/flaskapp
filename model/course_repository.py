from model.db import get_connection

def get_course_id_by_name(course_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM courses WHERE name=%s", (course_name,))
    row = cursor.fetchone()
    conn.close()
    return row["id"]
