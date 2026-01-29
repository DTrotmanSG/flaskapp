from flask import Flask
from controller.quiz_controller import quiz_blueprint
from controller.student_controller import student_blueprint

app = Flask(__name__, template_folder="view/templates")

app.register_blueprint(quiz_blueprint)
app.register_blueprint(student_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
