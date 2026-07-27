import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "recall_data.csv"
DATA_PATH2 = BASE_DIR / "data" / "car_faq.csv"
DATA_PATH3 = BASE_DIR / "crawled" / "recall_news_news_schema.csv"

# 제조사명 통일
MANUFACTURER_MAP = {
    "비엠더블유": "BMW",
    "폭스바겐그룹": "폭스바겐",
    "현대자동차": "현대",
    "기아자동차": "기아",
    "메르세데스벤츠코리아": "벤츠",
    "메르세데스-벤츠": "벤츠",
}

load_dotenv()

@st.cache_resource # 첫 호출시에만 만들고 그 다음은 캐싱
def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}?charset=utf8mb4"
    )


def seed_data():
    """CSV를 car_recall 테이블에 적재 (최초 1회만 직접 실행)"""
    df = pd.read_csv(DATA_PATH)
    engine = get_engine()

    if "manufacturer" in df.columns:
        df["manufacturer"] = (
            df["manufacturer"]
            .astype(str)
            .str.strip()
            .replace(MANUFACTURER_MAP)
        )

    df.to_sql(
        name="car_recall",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"{len(df)}건 적재 완료")

def seed_data2():
    """CSV를 faq 테이블에 적재 (최초 1회만 직접 실행)"""
    df = pd.read_csv(DATA_PATH2)
    engine = get_engine()
    df.to_sql(
        name="faq",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"{len(df)}건 적재 완료")

def seed_data3():
    """CSV를 뉴스 테이블에 적재 (최초 1회만 직접 실행)"""
    df = pd.read_csv(DATA_PATH3)
    engine = get_engine()
    df.to_sql(
        name="news",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"{len(df)}건 뉴스 적재 완료")


if __name__ == "__main__":
    seed_data()
    seed_data2()
    seed_data3()