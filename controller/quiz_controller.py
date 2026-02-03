import random
import re
from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from model.questions import questions
from model.course_repository import get_course_id_by_name
from model.student_repository import insert_student
from utils.name_utils import name_from_email
from weasyprint import HTML, CSS

quiz_blueprint = Blueprint("quiz", __name__)

# ---------------------------------------------------------
# SECTION DEFINITIONS
# ---------------------------------------------------------

VISIBLE_SECTIONS = [
    "skills_experience",
    "technical_aptitude",
    "work_style",
    "career_motivation",
    "personality_fit",
]

SECTION_LABELS = {
    "skills_experience": "Skills & Experience",
    "technical_aptitude": "Technical Aptitude",
    "work_style": "Work Style",
    "career_motivation": "Career Motivation",
    "personality_fit": "Personality Fit",
}

SECTION_DESCRIPTIONS = {
    "skills_experience": "This section evaluates your technical background and hands‑on experience with key technologies and platforms.",
    "technical_aptitude": "How you approach technical challenges and learning new concepts.",
    "work_style": "How you prefer to work and what environment helps you thrive.",
    "career_motivation": "What drives your career decisions and where you see yourself developing.",
    "personality_fit": "How you communicate, collaborate, and work with others.",
}

TRACK_TRANSLATION = {
    "infrastructure": "Infrastructure Engineering",
    "software": "Software Engineering",
    "data": "AI & Data Engineering",
    "business": "Business & Project Management",
    "cyber": "Cyber",
}

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def is_valid_name(name: str) -> bool:
    pattern = r"^[A-Za-zÀ-ÖØØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ\s\.'\-]{1,49}$"
    return bool(re.match(pattern, name.strip()))


def find_question_by_id(qid: int):
    for section_questions in questions.values():
        for q in section_questions:
            if q["id"] == qid:
                return q
    return None


def build_quiz_state():
    quiz_state = {
        "section_order": VISIBLE_SECTIONS.copy(),
        "question_order": {},
        "option_order": {},
        "answers": {},
    }

    hidden_questions = questions.get("track_alignment", [])
    hidden_assignment = {s: [] for s in VISIBLE_SECTIONS}

    for idx, q in enumerate(hidden_questions):
        section_name = VISIBLE_SECTIONS[idx % len(VISIBLE_SECTIONS)]
        hidden_assignment[section_name].append(q["id"])

    for section_name in VISIBLE_SECTIONS:
        base_questions = questions.get(section_name, [])
        base_ids = [q["id"] for q in base_questions]
        extra_ids = hidden_assignment.get(section_name, [])
        all_ids = base_ids + extra_ids
        random.shuffle(all_ids)
        quiz_state["question_order"][section_name] = all_ids

    for section_ids in quiz_state["question_order"].values():
        for qid in section_ids:
            q = find_question_by_id(qid)
            if not q:
                continue
            track_keys = list(q["options"].keys())
            random.shuffle(track_keys)
            quiz_state["option_order"][str(qid)] = track_keys

    return quiz_state

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@quiz_blueprint.route("/quiz")
def quiz_redirect():
    return redirect(url_for("quiz.quiz_start"))


@quiz_blueprint.route("/quiz/start", methods=["GET", "POST"])
def quiz_start():
    if "user_id" not in session:
        return redirect("/login")

    email = session.get("email")
    default_name = name_from_email(email) if email else ""

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()

        if not is_valid_name(student_name):
            return render_template(
                "quiz_intro.html",
                default_name=default_name,
                error="Please enter a valid name.",
            )

        session["student_name"] = student_name
        session["quiz_state"] = build_quiz_state()

        first_section = VISIBLE_SECTIONS[0]
        return redirect(url_for("quiz.quiz_section", section_name=first_section))

    return render_template("quiz_intro.html", default_name=default_name, error=None)


@quiz_blueprint.route("/quiz/section/<section_name>", methods=["GET"])
def quiz_section(section_name):
    if "user_id" not in session:
        return redirect("/login")

    quiz_state = session.get("quiz_state")
    if not quiz_state:
        return redirect(url_for("quiz.quiz_start"))

    if section_name not in VISIBLE_SECTIONS:
        return redirect(url_for("quiz.quiz_start"))

    section_order = quiz_state["section_order"]
    question_order = quiz_state["question_order"].get(section_name, [])
    option_order = quiz_state["option_order"]
    answers = quiz_state.get("answers", {})

    section_index = section_order.index(section_name)
    total_sections = len(section_order)

    questions_before = sum(
        len(quiz_state["question_order"][section_order[i]])
        for i in range(section_index)
    )

    next_section_label = None
    if section_index + 1 < total_sections:
        next_section_name = section_order[section_index + 1]
        next_section_label = SECTION_LABELS.get(next_section_name, next_section_name)

    letters = ["A", "B", "C", "D", "E"]
    questions_for_view = []

    for qid in question_order:
        q = find_question_by_id(qid)
        if not q:
            continue

        track_keys = option_order.get(str(qid), [])
        options = [
            {"letter": letters[i], "text": q["options"][track_key]}
            for i, track_key in enumerate(track_keys)
            if i < len(letters)
        ]

        questions_for_view.append({
            "id": q["id"],
            "text": q["text"],
            "options": options,
            "selected": answers.get(str(q["id"])),
        })

    return render_template(
        "quiz_section.html",
        section_name=section_name,
        section_label=SECTION_LABELS.get(section_name, section_name),
        section_description=SECTION_DESCRIPTIONS.get(section_name, ""),
        section_index=section_index,
        total_sections=total_sections,
        questions=questions_for_view,
        questions_before=questions_before,
        next_section_label=next_section_label,
        error=None,
    )


@quiz_blueprint.route("/quiz/submit_section", methods=["POST"])
def quiz_submit_section():
    if "user_id" not in session:
        return redirect("/login")

    quiz_state = session.get("quiz_state")
    if not quiz_state:
        return redirect(url_for("quiz.quiz_start"))

    section_name = request.form.get("section_name")
    if section_name not in VISIBLE_SECTIONS:
        return redirect(url_for("quiz.quiz_start"))

    section_order = quiz_state["section_order"]
    question_order = quiz_state["question_order"].get(section_name, [])
    answers = quiz_state.get("answers", {})

    missing = []

    for qid in question_order:
        field_name = f"q{qid}"
        answer_letter = request.form.get(field_name)

        if not answer_letter:
            missing.append(qid)
        else:
            answers[str(qid)] = answer_letter

    quiz_state["answers"] = answers
    session["quiz_state"] = quiz_state

    current_index = section_order.index(section_name)

    if missing:
        option_order = quiz_state["option_order"]
        letters = ["A", "B", "C", "D", "E"]
        questions_for_view = []

        for qid in question_order:
            q = find_question_by_id(qid)
            if not q:
                continue

            track_keys = option_order.get(str(qid), [])
            options = [
                {"letter": letters[i], "text": q["options"][track_key]}
                for i, track_key in enumerate(track_keys)
                if i < len(letters)
            ]

            questions_for_view.append({
                "id": q["id"],
                "text": q["text"],
                "options": options,
                "selected": answers.get(str(q["id"])),
                "is_missing": qid in missing,
            })

        questions_before = sum(
            len(quiz_state["question_order"][section_order[i]])
            for i in range(current_index)
        )

        next_section_label = None
        if current_index + 1 < len(section_order):
            next_section_name = section_order[current_index + 1]
            next_section_label = SECTION_LABELS.get(next_section_name, next_section_name)

        return render_template(
            "quiz_section.html",
            section_name=section_name,
            section_label=SECTION_LABELS.get(section_name, section_name),
            section_description=SECTION_DESCRIPTIONS.get(section_name, ""),
            section_index=current_index,
            total_sections=len(section_order),
            questions=questions_for_view,
            questions_before=questions_before,
            next_section_label=next_section_label,
            error="Please answer all questions before continuing.",
        )

    if current_index + 1 < len(section_order):
        next_section = section_order[current_index + 1]
        return redirect(url_for("quiz.quiz_section", section_name=next_section))

    return redirect(url_for("quiz.quiz_review"))


@quiz_blueprint.route("/quiz/review", methods=["GET"])
def quiz_review():
    if "user_id" not in session:
        return redirect("/login")

    quiz_state = session.get("quiz_state")
    if not quiz_state:
        return redirect(url_for("quiz.quiz_start"))

    section_order = quiz_state["section_order"]
    question_order = quiz_state["question_order"]
    option_order = quiz_state["option_order"]
    answers = quiz_state.get("answers", {})

    letters = ["A", "B", "C", "D", "E"]
    sections_for_view = []

    for section_name in section_order:
        section_questions_ids = question_order.get(section_name, [])
        section_questions_view = []

        for qid in section_questions_ids:
            q = find_question_by_id(qid)
            if not q:
                continue

            track_keys = option_order.get(str(qid), [])
            options = [
                {"letter": letters[i], "text": q["options"][track_key]}
                for i, track_key in enumerate(track_keys)
                if i < len(letters)
            ]

            selected_letter = answers.get(str(q["id"]))
            selected_text = None
            if selected_letter:
                for opt in options:
                    if opt["letter"] == selected_letter:
                        selected_text = opt["text"]
                        break

            section_questions_view.append({
                "id": q["id"],
                "text": q["text"],
                "selected_letter": selected_letter,
                "selected_text": selected_text,
            })

        sections_for_view.append({
            "name": section_name,
            "label": SECTION_LABELS.get(section_name, section_name),
            "questions": section_questions_view,
        })

    return render_template(
        "quiz_review.html",
        sections=sections_for_view,
    )


@quiz_blueprint.route("/quiz/results", methods=["GET"])
def quiz_results():
    if "user_id" not in session:
        return redirect("/login")

    quiz_state = session.get("quiz_state")
    if not quiz_state:
        return redirect(url_for("quiz.quiz_start"))

    option_order = quiz_state["option_order"]
    answers = quiz_state.get("answers", {})

    scores = {
        "Infrastructure Engineering": 0,
        "Software Engineering": 0,
        "AI & Data Engineering": 0,
        "Business & Project Management": 0,
        "Cyber": 0,
    }

    for qid_str, answer_letter in answers.items():
        track_keys = option_order.get(qid_str)
        if not track_keys:
            continue

        index = ord(answer_letter.upper()) - ord("A")
        if index < 0 or index >= len(track_keys):
            continue

        track_key = track_keys[index]
        track_name = TRACK_TRANSLATION.get(track_key)

        if track_name:
            scores[track_name] += 1

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    best_track = sorted_scores[0][0]
    second_track = sorted_scores[1][0]

    top_score = sorted_scores[0][1]
    second_score = sorted_scores[1][1]

    if top_score - second_score >= 3:
        confidence = "High Confidence"
    elif top_score - second_score >= 1:
        confidence = "Moderate Confidence"
    else:
        confidence = "Exploratory Match"

    TRACK_DESCRIPTIONS = {
        "Infrastructure Engineering": "Infrastructure Engineers design, build, and run the core technology services that underpin UBS’s digital products. They focus on reliability, operational excellence, cloud and on‑prem infrastructure, observability, and secure, scalable platforms.",
        "Software Engineering": "Software Engineers design, develop, and improve the digital products and services used by UBS clients and employees. They apply modern engineering practices, collaborate in agile teams, and build secure, high‑quality applications.",
        "AI & Data Engineering": "AI & Data Engineers create and manage data products, pipelines, and models that transform information into actionable insights. They work with databases, analytics, automation, and machine learning to support decision‑making across UBS.",
        "Business & Project Management": "Business & Project Management professionals support delivery, coordination, analysis, and stakeholder engagement across UBS Technology Services. They help teams understand requirements, manage risk, and deliver value.",
        "Cyber": "Cyber professionals protect UBS systems, data, and digital services through security engineering, risk management, and identity and access control. They focus on threat detection, secure design, and operational resilience.",
    }

    track_description = TRACK_DESCRIPTIONS.get(best_track, "")

    reasoning = (
        f"Your responses indicate strengths that align closely with the expectations of the {best_track} pathway. "
        f"You demonstrated patterns consistent with the core behaviours UBS looks for, including structured problem‑solving, "
        f"ownership of tasks, and a willingness to learn and develop. "
        f"Your preferences and working style also align with the competencies required for success in this track, "
        f"such as collaboration, adaptability, and a focus on delivering high‑quality outcomes."
    )

    user_id = session.get("user_id")
    student_name = session.get("student_name", "Student")
    track_id = get_course_id_by_name(best_track)
    insert_student(student_name, track_id, user_id)

    return render_template(
        "quiz_results.html",
        name=student_name,
        best_track=best_track,
        secondary_track=second_track,
        confidence=confidence,
        track_description=track_description,
        reasoning=reasoning,
        scores=sorted_scores,
    )


# ---------------------------------------------------------
# PDF EXPORT
# ---------------------------------------------------------

@quiz_blueprint.route("/quiz/export_pdf", methods=["GET"])
def quiz_export_pdf():
    if "user_id" not in session:
        return redirect("/login")

    quiz_state = session.get("quiz_state")
    if not quiz_state:
        return redirect(url_for("quiz.quiz_start"))

    option_order = quiz_state["option_order"]
    answers = quiz_state.get("answers", {})

    scores = {
        "Infrastructure Engineering": 0,
        "Software Engineering": 0,
        "AI & Data Engineering": 0,
        "Business & Project Management": 0,
        "Cyber": 0,
    }

    for qid_str, answer_letter in answers.items():
        track_keys = option_order.get(qid_str)
        if not track_keys:
            continue

        index = ord(answer_letter.upper()) - ord("A")
        if index < 0 or index >= len(track_keys):
            continue

        track_key = track_keys[index]
        track_name = TRACK_TRANSLATION.get(track_key)

        if track_name:
            scores[track_name] += 1

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    best_track = sorted_scores[0][0]
    second_track = sorted_scores[1][0]

    student_name = session.get("student_name", "Candidate")

    html = render_template(
        "pdf_results.html",
        name=student_name,
        best_track=best_track,
        secondary_track=second_track,
        scores=sorted_scores,
    )

    pdf = HTML(string=html).write_pdf(stylesheets=[CSS("static/pdf.css")])

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = 'attachment; filename="UBS_Track_Results.pdf"'
    return response
