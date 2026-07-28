import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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


def get_manufacturer_id(engine, manufacturer_name):
    """
    제조사 이름으로 manufacturer.id 조회
    """

    with engine.connect() as conn:
        manufacturer_id = conn.execute(
            text(
                """
                SELECT id
                FROM manufacturer
                WHERE name = :name
                """
            ),
            {"name": manufacturer_name},
        ).scalar()

    if manufacturer_id is None:
        raise ValueError(
            f"manufacturer 테이블에 '{manufacturer_name}' 데이터가 없습니다."
        )

    return manufacturer_id


def insert_service_center(
    csv_path,
    manufacturer_name,
    table_name="service_center",
):
    """
    서비스센터 CSV → MySQL INSERT

    Parameters
    ----------
    csv_path:
        CSV 파일 경로

    manufacturer_name:
        manufacturer 테이블에서 조회할 제조사명

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

    manufacturer_id = get_manufacturer_id(
        engine,
        manufacturer_name,
    )

    df.insert(0, "manufacturer_id", manufacturer_id)

    print(f"INSERT 시작 : {manufacturer_name} ({len(df)}건)")

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(f"INSERT 완료 : {manufacturer_name} ({len(df)}건)")


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[3]

    insert_service_center(
        ROOT / "crawled" / "service_center" / "benz_service_centers.csv",
        "벤츠",
    )

    insert_service_center(
        ROOT / "crawled" / "service_center" / "bmw_service_centers.csv",
        "BMW",
    )

    insert_service_center(
        ROOT / "crawled" / "service_center" / "volkswagen_service_centers.csv",
        "폭스바겐",
    )

    insert_service_center(
        ROOT / "crawled" / "service_center" / "hyundai_service_centers.csv",
        "현대",
    )

    insert_service_center(
        ROOT / "crawled" / "service_center" / "kia_service_centers.csv",
        "기아",
    )
