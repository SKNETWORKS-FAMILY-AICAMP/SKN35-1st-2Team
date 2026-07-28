"""
[1회성 테스트 & 데이터 시딩 스크립트]
crawled/recall_news_news_schema.csv 데이터를 MySQL news DB 테이블에 적재합니다.
파일명 규칙에 따라 'TEST'를 포함합니다.
"""

import os
import sys
from pathlib import Path
import pandas as pd

# src 디렉토리를 sys.path 최상단에 추가
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sqlalchemy import text
from db.connect_db import get_engine, DATA_PATH3


def seed_news():
    print(f"Reading CSV file from: {DATA_PATH3}")
    df = pd.read_csv(DATA_PATH3, encoding="utf-8")
    
    print(f"Loaded {len(df)} news rows.")
    print("Columns:", list(df.columns))

    # 결측치 처리
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["summary"] = df["summary"].fillna("").astype(str).str.strip()
    df["url"] = df["url"].fillna("").astype(str).str.strip()
    df["source"] = df["source"].fillna("국토교통부").astype(str).str.strip()
    df["published_at"] = df["published_at"].fillna("").astype(str).str.strip()

    engine = get_engine()
    
    print("Seeding news into MySQL 'news' table...")
    df.to_sql(
        name="news",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000,
    )

    # id 컬럼 AUTO_INCREMENT 설정 및 PRIMARY KEY 지정
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE news ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;"))
        conn.commit()

    print(f"Successfully seeded {len(df)} news records into 'news' table!")


if __name__ == "__main__":
    seed_news()
