import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="flaskuser",
        password="root root",
        database="flaskdb",
        cursorclass=pymysql.cursors.DictCursor
    )
