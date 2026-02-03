from flask import Blueprint, render_template, request, redirect, session
from model.db import get_connection

# Blueprint MUST be defined before any routes
home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def home():
    return render_template("home.html")


@home_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        # Validate domain
        if not email.endswith("@mthree.com"):
            return render_template("login.html", error="Email must be an @mthree.com address")

        db = get_connection()
        cursor = db.cursor()

        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            if user:
                user_id = user["id"]
            else:
                cursor.execute("INSERT INTO users (email) VALUES (%s)", (email,))
                db.commit()
                user_id = cursor.lastrowid

            # Store user session data
            session["user_id"] = user_id
            session["email"] = email

        finally:
            cursor.close()
            db.close()

        return redirect("/quiz")

    return render_template("login.html")


@home_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

