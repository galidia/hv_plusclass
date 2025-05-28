import json
import os
from datetime import datetime
import pytz

# 과목 축약어 매핑
subject_mapping = {
    "사회문화(3학년)": "사문",
    "한국지리(3학년)": "한지",
    "자습(3학년)": "자습",
    "생활과 윤리(3학년)": "생윤",
    "수능 독서 독해전략(3학년)": "독서",
    "수능특강 영어 독해와 작문(3학년)": "영독",
    "수능특강 수학(3학년-수학1)": "수1",
    "수능 문제분석(3학년-수학2)": "수2",
    "수능특강 영어(3학년)": "영어",
    "생명과학(3학년)": "생명",
    "지구과학(3학년)": "지구",
    "화학(3학년)": "화학",
    "물리학(3학년)": "물리",
    "문학 총정리(3학년)": "문학"
}

# 요일 영어 → 한글 매핑
weekday_kor = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
}

def get_timetable(student_id: str) -> str:
    # 파일 경로 설정
    student_path = r"C:\Users\jakeu\OneDrive\Desktop\pythoncordingfile\bochung\사람당 보충.json"
    schedule_path = r"C:\Users\jakeu\OneDrive\Desktop\pythoncordingfile\bochung\보충시간표_원래날짜_요일완전복원.json"

    # 파일 존재 여부 확인
    if not os.path.exists(student_path) or not os.path.exists(schedule_path):
        return "필요한 JSON 파일이 존재하지 않습니다."

    # JSON 파일 불러오기
    with open(student_path, encoding="utf-8") as f:
        student_data = json.load(f)

    with open(schedule_path, encoding="utf-8") as f:
        schedule_data = json.load(f)

    # 날짜 포맷 조정 (0 제거)
    tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(tz)
    weekday = weekday_kor[now.strftime('%A')]
    month = now.strftime('%m').lstrip('0')
    day = now.strftime('%d').lstrip('0')
    today_str = f"{now.year}년 {month}월 {day}일 {weekday}"

    # 학번 정보 가져오기
    student = student_data.get(student_id)
    if not student:
        return "해당 학번의 학생 정보를 찾을 수 없습니다."

    today_schedule = schedule_data.get(today_str)
    if not today_schedule:
        return f"{today_str}은(는) 보충 수업이 없습니다."

    # 8, 9교시 분석
    result_list = []
    for period in ["8", "9"]:
        entry = next((item for item in today_schedule if item["교시"] == period), None)
        if not entry:
            continue

        code = entry.get("코드")
        subject_full = student["수업"].get(code)
        if not subject_full:
            continue

        subject_short = subject_mapping.get(subject_full, subject_full)
        class_dict = entry.get("수업", {})

        # 양쪽 모두 축약어 기반으로 비교
        matching_class = [
            cls for cls, subj in class_dict.items()
            if subject_mapping.get(subj, subj) == subject_short
        ]

        if matching_class:
            result_list.append(f"{period}교시는 {subject_short} {matching_class[0]}")

    return ", ".join(result_list) + "입니다." if result_list else "해당 교시에는 수업이 없습니다."


# 실행부
if __name__ == "__main__":
    student_id = input("학번을 입력하세요: ").strip()
    result = get_timetable(student_id)
    print(result)
