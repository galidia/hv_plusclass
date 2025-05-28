from flask import Flask, render_template, request
from bochung import get_timetable  # 기존 코드에서 함수 가져옴
import os


app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    student_id = request.form["student_id"]
    result_text = get_timetable(student_id)
    return render_template("result.html", result=result_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render에서 제공하는 포트
    app.run(host="0.0.0.0", port=port)

