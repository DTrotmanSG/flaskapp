from model.db import get_connection

def insert_student(name, track_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO students (student_name, course_id) VALUES (%s, %s)"
    cursor.execute(query, (name, track_id))

    conn.commit()
    cursor.close()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            students.student_name,
            courses.name AS track_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
        ORDER BY students.id DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows
