# crawling 해온 데이터(csv 파일)을 service_center 테이블에 저장

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_db_engine():
    """
    MySQL DB Engine 생성
    """

    return create_engine(
        f"mysql+pymysql://"
        f"{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_DATABASE')}"
        f"?charset=utf8mb4"
    )


def fix_coordinates(df):
    """
    위도/경도 데이터 오류 보정

    latitude 값이 90 이상이면
    latitude와 longitude가 뒤바뀐 데이터로 판단
    """

    if "latitude" not in df.columns or "longitude" not in df.columns:
        return df

    mask = df["latitude"] > 90

    if mask.any():
        temp = df.loc[mask, "latitude"].copy()

        df.loc[mask, "latitude"] = df.loc[mask, "longitude"]

        df.loc[mask, "longitude"] = temp

        print(f"좌표 보정 완료 : {mask.sum()}건")

    return df


def insert_service_center(
    csv_path,
    table_name="service_center",
):
    """
    서비스센터 CSV → MySQL INSERT

    Parameters
    ----------
    csv_path:
        CSV 파일 경로

    table_name:
        저장할 테이블명
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일 없음 : {csv_path}")

    print(f"CSV 읽기 : {csv_path}")

    df = pd.read_csv(csv_path)

    df = fix_coordinates(df)

    engine = get_db_engine()

    print(f"INSERT 시작 : {len(df)}건")

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(f"INSERT 완료 : {len(df)}건")


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[2]

    insert_service_center(ROOT / "crawled" / "benz_service_centers.csv")
    insert_service_center(ROOT / "crawled" / "bmw_service_centers.csv")
    insert_service_center(ROOT / "crawled" / "volkswagen_service_centers.csv")
    insert_service_center(ROOT / "crawled" / "hyundai_service_centers.csv")
    insert_service_center(ROOT / "crawled" / "kia_service_centers.csv")
