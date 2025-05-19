from flask import Flask, request, jsonify
from datetime import datetime
import json
import pandas as pd

app = Flask(__name__)

# 1. 사용자 정보 불러오기
def load_students():
    with open("students.json", encoding="utf-8") as f:
        return json.load(f)

# 2. 사용자 정보 저장하기
def save_students(data):
    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 3. 오늘 날짜에 해당하는 시간표 불러오기
def get_today_schedule():
    df = pd.read_excel("schedule.xlsx")
    today = datetime.now().strftime("%Y-%m-%d")
    row = df[df["날짜"].astype(str).str.startswith(today)]
    if row.empty:
        return None
    return row.iloc[0]  # 해당 날짜의 row 반환

# 4. 메인 응답 처리 함수
@app.route("/message", methods=["POST"])
def message():
    req = request.get_json()
    user_id = req["userRequest"]["user"]["id"]
    utter = req["userRequest"]["utterance"].strip()

    students = load_students()

    # 1️⃣ 사용자 등록 처리
    if user_id not in students:
        # 등록 시: "6반 7번 서준우"
        if "반" in utter and "번" in utter:
            parts = utter.replace("반", "").replace("번", "").split()
            if len(parts) == 3:
                class_num, student_num, name = parts
                students[user_id] = {
                    "반": class_num,
                    "번호": student_num,
                    "이름": name,
                    "A": "수학1", "B": "영독", "C": "물리학", "D": "수학2", "E": "생명과학", "F": "자습"
                }
                save_students(students)
                text = f"{name}님 등록 완료!\n이제 '오늘 보충'이라고 입력해보세요."
            else:
                text = "형식에 맞게 입력해주세요. 예: 6반 7번 서준우"
        else:
            text = "안녕하세요! 이름과 학번을 알려주세요. 예: 6반 7번 서준우"
        return jsonify(make_simple_response(text))

    # 2️⃣ 오늘 보충 요청
    if "오늘 보충" in utter:
        user = students[user_id]
        sched = get_today_schedule()
        if sched is None:
            return jsonify(make_simple_response("오늘은 보충 수업이 없습니다."))

        # 현재 사용자 반 정보로 해당 반 수업 확인
        cls = int(user["반"])
        class_col = f"Unnamed: {cls + 3}"  # 예: 6반 → Unnamed: 9
        subject_8 = sched[class_col] if sched["교시"] == 8 else None
        subject_9 = sched[class_col] if sched["교시"] == 9 else None

        code_to_subject = {k: user[k] for k in "ABCDEF"}

        result = "[오늘 보충 수업 안내]\n"
        if subject_8:
            result += f"8교시: {code_to_subject.get(subject_8, '정보 없음')} - {cls}반\n"
        if subject_9:
            result += f"9교시: {code_to_subject.get(subject_9, '정보 없음')} - {cls}반\n"

        return jsonify(make_simple_response(result))

    return jsonify(make_simple_response("잘 이해하지 못했어요. '오늘 보충'이라고 입력해보세요."))

# 응답 포맷 JSON 만들기
def make_simple_response(text):
    return {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {"text": text}
            }],
            "quickReplies": [
                {
                    "label": "오늘 보충",
                    "action": "message",
                    "messageText": "오늘 보충"
                }
            ]
        }
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
