import random
from flask import Blueprint, render_template, request, session
from model.questions import questions
from model.course_repository import get_course_id_by_name
from model.student_repository import insert_student

quiz_blueprint = Blueprint("quiz", __name__)

@quiz_blueprint.route("/quiz")
def quiz():
    # 1. Shuffle questions
    shuffled_questions = questions.copy()
    random.shuffle(shuffled_questions)

    # 2. Shuffle answer order per question
    for q in shuffled_questions:
        items = list(q["options"].items())  # (track, text)
        random.shuffle(items)
        q["shuffled_options"] = items

    # 3. Randomize answer-letter → track mapping
    tracks = ["infrastructure", "software", "data", "business", "cyber"]
    random.shuffle(tracks)

    answer_map = {
        "A": tracks[0],
        "B": tracks[1],
        "C": tracks[2],
        "D": tracks[3],
        "E": tracks[4]
    }

    session["answer_map"] = answer_map
    session["question_order"] = [q["id"] for q in shuffled_questions]

    return render_template("quiz.html", questions=shuffled_questions)


@quiz_blueprint.route("/quiz", methods=["POST"])
def quiz_submit():
    name = request.form.get("student_name")
    answer_map = session.get("answer_map")

    # Initialize scoring buckets
    scores = {
        "Infrastructure Engineering": 0,
        "Software Engineering": 0,
        "AI & Data Engineering": 0,
        "Business & Project Management": 0,
        "Cyber": 0
    }

    track_translation = {
        "infrastructure": "Infrastructure Engineering",
        "software": "Software Engineering",
        "data": "AI & Data Engineering",
        "business": "Business & Project Management",
        "cyber": "Cyber"
    }

    # Score each question
    for qid in session.get("question_order", []):
        answer_letter = request.form.get(f"q{qid}")
        if not answer_letter:
            continue

        track_key = answer_map.get(answer_letter)
        track_name = track_translation.get(track_key)

        if track_name:
            scores[track_name] += 1

    # Determine best track
    best_track = max(scores, key=scores.get)
    track_id = get_course_id_by_name(best_track)

    insert_student(name, track_id)

    return render_template("result.html", name=name, best_track=best_track)
