from flask import Flask
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="flaskuser",
        password="root root",
        database="flaskdb",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return "Hello from your EC2 Flask App!"

@app.route("/students")
def students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, course FROM students")
    rows = cursor.fetchall()
    conn.close()

    output = "<h2>Student List</h2>"
    for row in rows:
        output += f"<p>{row['name']} — {row['course']}</p>"
    return output

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

