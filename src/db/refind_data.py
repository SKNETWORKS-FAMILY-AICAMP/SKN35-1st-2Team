# ==========================================================
# 정제된 데이터에서 용도에 맞게 필터링 하도록 가져오는 파일
# 함수 인자로 설정값을 보내주고 그거에 맞게 select 해서 가져오기
# ==========================================================
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

# ============== 검색 ==============
def search_recall(manufacturer=None, model=None, keyword=None):
    engine = get_engine()

    sql = """
    SELECT
        manufacturer AS 제작자,
        model_name AS 차명,
        production_start AS 생산기간_부터,
        production_end AS 생산기간_까지,
        recall_start_date AS 리콜개시일,
        recall_count AS 리콜대수,
        recall_reason AS 리콜사유
    FROM car_recall
    WHERE 1=1
    """

    params = {}

    if manufacturer and manufacturer != "전체":
        sql += " AND manufacturer LIKE :manufacturer"
        params["manufacturer"] = f"%{manufacturer}%"

    if model:
        sql += " AND model_name LIKE :model"
        params["model"] = f"%{model}%"

    if keyword:
        sql += " AND recall_reason LIKE :keyword"
        params["keyword"] = f"%{keyword}%"

    sql += " ORDER BY recall_start_date DESC"

    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)