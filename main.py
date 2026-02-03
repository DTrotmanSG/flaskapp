from flask import Flask
from datetime import timedelta

from controller.home_controller import home_blueprint
from controller.quiz_controller import quiz_blueprint
from controller.student_controller import student_blueprint

app = Flask(__name__, template_folder="view/templates")

# SECURITY: Replace this with a real secret key in production
app.secret_key = "super-secret-key-change-this"

# SESSION TIMEOUT: Auto‑logout after 20 minutes of inactivity
app.permanent_session_lifetime = timedelta(minutes=20)

# Make Python's zip() available inside Jinja templates
app.jinja_env.globals.update(zip=zip)

# Register blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(quiz_blueprint)
app.register_blueprint(student_blueprint)

if __name__ == "__main__":
    # Run the sandbox version on a different port so it never clashes with the live app
    app.run(host="0.0.0.0", port=5001)
