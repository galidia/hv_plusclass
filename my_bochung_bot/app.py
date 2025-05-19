from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# 엑셀 파일 경로
BOCHUNG_PATH = "bochung_data.xlsx"
TIMETABLE_PATH = "timetable_data.xlsx"

# 데이터 불러오기
bochung_df = pd.read_excel(BOCHUNG_PATH, sheet_name='Sheet1')
timetable_df = pd.read_excel(TIMETABLE_PATH, sheet_name='3학년', header=3)

# 사용자 정보 저장 (간단한 메모리 기반)
user_data = {}  # chat_id: {'이름': 이름, '반': 반, '번호': 번호}

# 수업코드 매칭용 역변환 dict
def get_user_classes(name, ban, number):
    result = {}
    row = bochung_df[(bochung_df["이름"] == name) & (bochung_df["반"] == ban) & (bochung_df["번호"] == number)]
    if row.empty:
        return result
    row = row.iloc[0]
    for subject in row.index:
        if subject not in ['순번', '학년', '반', '번호', '이름'] and pd.notna(row[subject]):
            code = row[subject]
            result[code] = subject.replace("(3학년)", "").strip()
    return result

# 오늘 날짜로 시간표 필터
def get_today_schedule(user_info):
    today = datetime.now().strftime("%-m/%-d")  # 예: '5/19'
    today_row = timetable_df[timetable_df['요일'] == today]
    if today_row.empty:
        return "오늘은 수업이 없습니다."
    
    name, ban, number = user_info['이름'], user_info['반'], user_info['번호']
    user_classes = get_user_classes(name, ban, number)

    result = []
    for period in ['8교시', '9교시']:
        value = today_row[period].values[0]  # 예: "F-6"
        if pd.isna(value) or '-' not in value:
            continue
        code, class_num = value.split('-')
        if code in user_classes:
            result.append(f"{period}: {user_classes[code]}-{class_num}반")
    return "\n".join(result) if result else "오늘은 보충 수업이 없습니다."

@app.route("/message", methods=["POST"])
def kakao_message():
    data = request.json
    chat_id = data['userRequest']['user']['id']
    utter = data['userRequest']['utterance'].strip()

    # 사용자 초기 등록
    if chat_id not in user_data:
        if "이름" in utter and "번" in utter:
            try:
                # 예: 서준우 6반 7번
                name, ban, num = utter.split()
                ban = int(ban.replace("반", ""))
                num = int(num.replace("번", ""))
                user_data[chat_id] = {'이름': name, '반': ban, '번호': num}
                return jsonify(make_response(f"{name}님 정보를 저장했어요. '오늘 보충'이라고 입력해보세요."))
            except:
                return jsonify(make_response("올바른 형식: 이름 6반 7번"))
        else:
            return jsonify(make_response("처음이시군요! '이름 6반 7번'처럼 입력해주세요."))

    # 정보 입력 후
    if "오늘 보충" in utter:
        response = get_today_schedule(user_data[chat_id])
        return jsonify(make_response(response))

    return jsonify(make_response("잘 이해하지 못했어요. '오늘 보충' 또는 '이름 6반 7번'처럼 입력해주세요."))

# 카카오 응답 포맷
def make_response(text):
    return {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": text
                }
            }]
        }
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
