import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "recall_data.csv"

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
    df.to_sql(
        name="car_recall",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"{len(df)}건 적재 완료")


if __name__ == "__main__":
    seed_data()