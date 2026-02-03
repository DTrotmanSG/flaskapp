from model.db import get_connection

def insert_student(name, course_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO students (name, course_id, user_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            course_id = VALUES(course_id)
    """

    cursor.execute(query, (name, course_id, user_id))
    conn.commit()

    cursor.close()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            students.name AS name,
            courses.name AS track_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
        ORDER BY students.id DESC
    """

    cursor.execute(query)
    results = cursor.fetchall()

    students = []
    for row in results:
        students.append({
            "student_name": row["name"],
            "track_name": row["track_name"]
        })

    cursor.close()
    conn.close()

    return students
