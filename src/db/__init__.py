# DB 관련

import os

import mysql.connector
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT")),
    )


def init_db():
    """테이블이 없을 경우 초기 생성합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE service_center (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL COMMENT '서비스센터명',
        address VARCHAR(255) NOT NULL COMMENT '주소',
        phone VARCHAR(30) COMMENT '전화번호',
        latitude DECIMAL(10,8) NOT NULL COMMENT '위도',
        longitude DECIMAL(11,8) NOT NULL COMMENT '경도',

        INDEX idx_name (name)
    ) ENGINE=InnoDB
    DEFAULT CHARSET=utf8mb4
    COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    cursor.close()
    conn.close()
