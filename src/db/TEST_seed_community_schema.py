"""
[1회성 테스트 & 데이터 시딩 스크립트]
ERD 기반 스키마(manufacturer, car_model, posts, comments, news)를 초기화하고 샘플 데이터를 시딩합니다.
파일명 규칙에 따라 'TEST'를 포함합니다.
"""

import os
import sys
from pathlib import Path

# src 디렉토리를 sys.path 최상단에 추가
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db.db_utils import init_db, get_conn, get_or_create_manufacturer, get_or_create_car_model, add_post


def run_seed():
    print("1. Initializing DB schema (manufacturer, car_model, posts, comments, news)...")
    init_db()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    print("2. Checking posts count...")
    cur.execute("SELECT COUNT(*) as c FROM posts")
    res = cur.fetchone()
    count = res['c'] if res else 0

    if count == 0:
        print("Seeding sample community posts...")
        sample_posts = [
            ("그랜저 하이브리드 엔진 경고등 문제 관련 공유합니다", "주행 중 엔진 경고등이 점등되어 블루핸즈 방문 결과 무상 소프트웨어 업데이트 조치 받았습니다.", "현대", "그랜저", "엔진/파워트레인", "차모아유저1", "1234"),
            ("쏘렌토 브레이크 이음 발생 해결 후기", "브레이크 밟을 때 소리가 나서 오토큐 방문 후 패드 점검 및 클리닝 조치 완료했습니다.", "기아", "쏘렌토", "브레이크/제동", "안전운전짱", "1234"),
            ("벤츠 E클래스 인포테인먼트 멈춤 현상 조치법", "MBUX 화면이 꺼지는 현상이 있어 서비스센터 무상 점검 받았네요.", "벤츠", "E-Class", "소프트웨어", "벤츠매니아", "1234"),
            ("BMW 5시리즈 리콜 예약 방법 문의", "공식 서비스센터 앱으로 리콜 예약 가능한지 궁금합니다.", "BMW", "5시리즈", "기타", "비머러버", "1234"),
        ]
        for title, content, brand, model, category, author, password in sample_posts:
            add_post(
                title=title,
                content=content,
                brand=brand,
                model=model,
                category=category,
                author=author,
                password=password
            )
        print(f"Successfully seeded {len(sample_posts)} sample posts!")
    else:
        print(f"Posts table already has {count} posts.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    run_seed()
