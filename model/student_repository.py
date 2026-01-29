from model.db import get_connection

def insert_student(name, course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, course_id) VALUES (%s, %s)",
        (name, course_id)
    )
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT students.name AS student_name, courses.name AS course_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
