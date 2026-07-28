"""
MySQL (car_recall DB) posts 테이블에 10개의 커뮤니티 더미데이터를 직접 생성하는 스크립트
"""

import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_DATABASE", "car_recall"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


def seed_posts():
    dummy_posts = [
        {
            "title": "아반떼 CN7 무상수리 받고 온 후기 공유합니다",
            "content": "엔진경고등 점등 문제로 공식 서비스센터 방문했는데 친절하게 ECU 업데이트와 센서 교체 무상 처리 받았습니다. 다들 이상 있으시면 미루지 말고 방문하세요!",
            "brand": "현대",
            "model": "아반떼 CN7",
            "category": "엔진/파워트레인",
            "author": "아반떼러버",
            "password": "1234",
            "created_at": "2026-07-25 10:15",
            "updated_at": "2026-07-25 10:15",
            "likes": 5,
        },
        {
            "title": "K5 하이브리드 배터리 경고등 관련 무상점검 정보",
            "content": "최근 고전압 배터리 제어시스템(BMS) 소프트웨어 업데이트 리콜 통지서 받아서 정비받고 왔습니다. 작업 시간은 30분 정도 소요되네요.",
            "brand": "기아",
            "model": "K5 하이브리드",
            "category": "전기/배터리",
            "author": "드라이버K",
            "password": "1234",
            "created_at": "2026-07-25 11:30",
            "updated_at": "2026-07-25 11:30",
            "likes": 8,
        },
        {
            "title": "제네시스 G80 브레이크 패드 소음 리콜 대상 확인법",
            "content": "제네시스 고객센터 어플이나 자동차리콜센터 웹사이트에서 차대번호 입력하시면 본인 차량이 해당 리콜 대상인지 바로 확인 가능합니다.",
            "brand": "제네시스",
            "model": "G80",
            "category": "브레이크/제동",
            "author": "럭셔리세단",
            "password": "1234",
            "created_at": "2026-07-25 12:45",
            "updated_at": "2026-07-25 12:45",
            "likes": 3,
        },
        {
            "title": "BMW 520d EGR 쿨러 관련 자발적 리콜 통지서 수령",
            "content": "EGR 쿨러 누유 가능성 건으로 리콜 통지서 접수했습니다. 부품 수급에 시간이 걸릴 수 있으니 미리 예약 잡으시는 것을 추천합니다.",
            "brand": "BMW",
            "model": "520d",
            "category": "엔진/파워트레인",
            "author": "비머매니아",
            "password": "1234",
            "created_at": "2026-07-25 13:20",
            "updated_at": "2026-07-25 13:20",
            "likes": 12,
        },
        {
            "title": "벤츠 E클래스 에어백 모듈 점검 후기",
            "content": "운전석 에어백 모듈 관련 점검 다녀왔습니다. 점검 결과 이상 없어서 안심하고 운행 중입니다.",
            "brand": "벤츠",
            "model": "E300",
            "category": "에어백/안전장치",
            "author": "삼각별사랑",
            "password": "1234",
            "created_at": "2026-07-25 14:10",
            "updated_at": "2026-07-25 14:10",
            "likes": 2,
        },
        {
            "title": "테슬라 모델3 오토파일럿 무상 업데이트 후기",
            "content": "OTA 무선 업데이트로 리콜 조치가 완료되어 서비스센터 방문 없이 집에서 편하게 조치받았습니다. 역시 소프트웨어 업데이트가 편하네요.",
            "brand": "테슬라",
            "model": "Model 3",
            "category": "소프트웨어",
            "author": "테슬라유저",
            "password": "1234",
            "created_at": "2026-07-25 15:05",
            "updated_at": "2026-07-25 15:05",
            "likes": 15,
        },
        {
            "title": "KG모빌리티 토레스 브레이크 호스 교환 조치 완료",
            "content": "브레이크 호스 고정 상태 점검 및 관련 부품 교체 무상수리 받았습니다. 정비사분들이 꼼꼼하게 봐주셨네요.",
            "brand": "KG모빌리티",
            "model": "토레스",
            "category": "브레이크/제동",
            "author": "토레스오너",
            "password": "1234",
            "created_at": "2026-07-25 16:00",
            "updated_at": "2026-07-25 16:00",
            "likes": 4,
        },
        {
            "title": "쉐보레 트랙스 크로스오버 소프트웨어 리콜 예약 방법",
            "content": "계기판 화면 일시적 오작동 가능성으로 인포테인먼트 소프트웨어 리콜 진행 중입니다. 가까운 쉐보레 서비스센터로 전화 예약 후 방문하세요.",
            "brand": "쉐보레",
            "model": "트랙스 크로스오버",
            "category": "소프트웨어",
            "author": "쉐비크루",
            "password": "1234",
            "created_at": "2026-07-25 17:30",
            "updated_at": "2026-07-25 17:30",
            "likes": 6,
        },
        {
            "title": "르노코리아 QM6 연료펌프 관련 조치 문의드립니다",
            "content": "연료펌프 관련 리콜 통지받으신 분들 혹시 당일 정비 가능했는지 궁금합니다. 예약 대기가 길어서 고민이네요.",
            "brand": "르노코리아",
            "model": "QM6",
            "category": "기타",
            "author": "큐엠식스",
            "password": "1234",
            "created_at": "2026-07-25 18:20",
            "updated_at": "2026-07-25 18:20",
            "likes": 1,
        },
        {
            "title": "전기차 고전압 배터리 관리 시스템 점검 팁 공유",
            "content": "전기차 차주분들은 정기점검 시 BMS 소프트웨어 버전 꼭 확인해달라고 하세요. 최신 버전으로 업데이트받아야 배터리 안정성이 향상됩니다.",
            "brand": "기아",
            "model": "EV6",
            "category": "전기/배터리",
            "author": "볼트맨",
            "password": "1234",
            "created_at": "2026-07-25 19:10",
            "updated_at": "2026-07-25 19:10",
            "likes": 9,
        },
    ]

    conn = get_conn()
    cur = conn.cursor()

    sql = """
        INSERT INTO posts (title, content, brand, model, category, author, password, created_at, updated_at, likes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for p in dummy_posts:
        cur.execute(
            sql,
            (
                p["title"],
                p["content"],
                p["brand"],
                p["model"],
                p["category"],
                p["author"],
                p["password"],
                p["created_at"],
                p["updated_at"],
                p["likes"],
            ),
        )

    conn.commit()
    inserted_count = len(dummy_posts)
    cur.close()
    conn.close()

    print(f"[SUCCESS] MySQL posts 테이블에 더미 데이터 {inserted_count}개가 성공적으로 저장되었습니다.")


if __name__ == "__main__":
    seed_posts()
