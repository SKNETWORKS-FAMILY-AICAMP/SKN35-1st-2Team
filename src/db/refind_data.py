import pandas as pd
from sqlalchemy import text
from db.connect_db import get_engine

# ==============년도별 리콜건수==============
def get_yearly_recall(company: str, start: int, end: int) -> pd.DataFrame:
    engine = get_engine()
    query = text("""
        SELECT
            YEAR(recall_start_date) AS 년도,
            COUNT(*) AS 리콜건수
        FROM car_recall
        WHERE manufacturer LIKE :company
          AND YEAR(recall_start_date) BETWEEN :start AND :end
        GROUP BY YEAR(recall_start_date)
        ORDER BY 년도
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={
                "company": f"%{company}%",
                "start": start,
                "end": end
            }
        )

    return df.set_index("년도")


# ==============차종별 리콜건수==============
def get_car_model_recall(company: str, start: int, end: int) -> pd.DataFrame:
    engine = get_engine()
    query = text("""
        SELECT
            model_name AS 차명,
            COUNT(*) AS 리콜건수
        FROM car_recall
        WHERE manufacturer LIKE :company
          AND YEAR(recall_start_date) BETWEEN :start AND :end
        GROUP BY model_name
        ORDER BY 리콜건수 DESC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={
                "company": f"%{company}%",
                "start": start,
                "end": end
            }
        )

    return df.set_index("차명")


# ==============최근 3년 리콜건수 추세==============
def get_risk_trend(company: str) -> pd.DataFrame:
    engine = get_engine()
    query = text("""
        SELECT
            YEAR(recall_start_date) AS 년도,
            COUNT(*) AS 리콜건수
        FROM car_recall
        WHERE manufacturer LIKE :company
          AND YEAR(recall_start_date) >= YEAR(CURDATE()) - 2
        GROUP BY YEAR(recall_start_date)
        ORDER BY 년도
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={
                "company": f"%{company}%"
            }
        )

    return df.set_index("년도")