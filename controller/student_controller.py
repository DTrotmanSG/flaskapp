from flask import Blueprint, render_template
from model.student_repository import get_all_students

student_blueprint = Blueprint("students", __name__)

@student_blueprint.route("/students")
def students():
    students = get_all_students()
    return render_template("students.html", students=students)
