from flask import Blueprint, render_template, request
from model.course_repository import get_course_id_by_name
from model.student_repository import insert_student

quiz_blueprint = Blueprint("quiz", __name__)

@quiz_blueprint.route("/")
def home():
    return render_template("home.html")

@quiz_blueprint.route("/quiz")
def quiz():
    return render_template("quiz.html")

@quiz_blueprint.route("/quiz", methods=["POST"])
def quiz_submit():
    name = request.form.get("student_name")

    cloud = 0
    python = 0
    linux = 0

    answers = [
        request.form.get("q1"),
        request.form.get("q2"),
        request.form.get("q3")
    ]

    for answer in answers:
        if answer == "cloud":
            cloud += 1
        elif answer == "python":
            python += 1
        elif answer == "linux":
            linux += 1

    scores = {
        "Cloud Computing": cloud,
        "Python Development": python,
        "Linux Administration": linux
    }

    best_course = max(scores, key=scores.get)
    course_id = get_course_id_by_name(best_course)

    insert_student(name, course_id)

    return render_template("result.html", name=name, best_course=best_course)
