# 전국 법정동 csv파일의 데이터를 legal_dong 테이블에 필요한 데이터만 정제하여 저장

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}?charset=utf8mb4"
)


def insert_legal_dong():
    csv_path = Path("data/국토교통부_전국 법정동_20260630.csv")

    df = pd.read_csv(
        csv_path,
        encoding="utf-8",
        dtype=str,
    )

    # 필요한 컬럼만 선택
    df = df[
        [
            "시도명",
            "시군구명",
            "읍면동명",
            "리명",
        ]
    ]

    # NaN -> None
    df = df.where(pd.notna(df), None)

    df.columns = [
        "sido_name",
        "sigungu_name",
        "eupmyeondong_name",
        "ri_name",
    ]

    df.to_sql(
        name="legal_dong",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )

    print(f"{len(df)}건 저장 완료")


if __name__ == "__main__":
    insert_legal_dong()
