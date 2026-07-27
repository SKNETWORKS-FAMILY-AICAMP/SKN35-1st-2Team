# ==========================================================
# 정제된 데이터에서 용도에 맞게 필터링 하도록 가져오는 파일
# 함수 인자로 설정값을 보내주고 그거에 맞게 select 해서 가져오기
# ==========================================================

import pandas as pd
from sqlalchemy import text
from db.connect_db import get_engine

# ============== 기업 목록 ==============
def get_company_list():
    engine = get_engine()

    query = text("""
        SELECT name
        FROM manufacturer
        ORDER BY name
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df["name"].tolist()

# ========= 최소년도 & 최대년도 =========
def get_year_range(companies):
    if not companies:
        return None, None

    engine = get_engine()

    placeholders = ",".join(f":c{i}" for i in range(len(companies)))

    query = text(f"""
        SELECT
            MIN(YEAR(cr.recall_start_date)) AS min_year,
            MAX(YEAR(cr.recall_start_date)) AS max_year
        FROM car_recall cr
        JOIN car_model cm ON cr.car_model_id = cm.id
        JOIN manufacturer m ON cm.manufacturer_id = m.id
        WHERE m.name IN ({placeholders})
    """)

    params = {f"c{i}": company for i, company in enumerate(companies)}

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)

    if df.empty or pd.isna(df.loc[0, "min_year"]):
        return None, None

    return int(df.loc[0, "min_year"]), int(df.loc[0, "max_year"])

# ============== 년도별 리콜건수 ==============
def get_yearly_recall(company, start, end):
    engine = get_engine()

    query = text("""
        SELECT
            YEAR(cr.recall_start_date) AS 년도,
            COUNT(*) AS 리콜건수
        FROM car_recall cr
        JOIN car_model cm ON cr.car_model_id = cm.id
        JOIN manufacturer m ON cm.manufacturer_id = m.id
        WHERE m.name = :company
          AND YEAR(cr.recall_start_date) BETWEEN :start AND :end
        GROUP BY YEAR(cr.recall_start_date)
        ORDER BY 년도
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={
                "company": company,
                "start": start,
                "end": end
            }
        )

    return df.set_index("년도")

# ============== 차종별 리콜건수 ==============
def get_car_model_recall(company, start, end):
    engine = get_engine()

    query = text("""
        SELECT
            cm.name AS 차명,
            COUNT(*) AS 리콜건수
        FROM car_recall cr
        JOIN car_model cm ON cr.car_model_id = cm.id
        JOIN manufacturer m ON cm.manufacturer_id = m.id
        WHERE m.name = :company
          AND YEAR(cr.recall_start_date) BETWEEN :start AND :end
        GROUP BY cm.name
        ORDER BY 리콜건수 DESC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={
                "company": company,
                "start": start,
                "end": end
            }
        )

    return df.set_index("차명")

# ============== 최근 3년 리콜건수 추세 ==============
def get_risk_trend(company):
    engine = get_engine()

    query = text("""
        SELECT
            DATE_FORMAT(cr.recall_start_date, '%Y-%m') AS 연월,
            COUNT(*) AS 리콜건수
        FROM car_recall cr
        JOIN car_model cm ON cr.car_model_id = cm.id
        JOIN manufacturer m ON cm.manufacturer_id = m.id
        WHERE m.name = :company
          AND cr.recall_start_date >= DATE_SUB(
                (SELECT MAX(recall_start_date) FROM car_recall),
                INTERVAL 2 YEAR
          )
        GROUP BY DATE_FORMAT(cr.recall_start_date, '%Y-%m')
        ORDER BY DATE_FORMAT(cr.recall_start_date, '%Y-%m')
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"company": company})

    return df.set_index("연월")

# ============== 타이틀 용도 (증가량, 대수) ==============
def get_latest_trend():
    engine = get_engine()

    query = text("""
        SELECT
            YEAR(recall_start_date) AS 년도,
            COUNT(*) AS 리콜건수,
            SUM(recall_count) AS 리콜대상차량수
        FROM car_recall
        WHERE YEAR(recall_start_date) >= (
            SELECT MAX(YEAR(recall_start_date)) - 1
            FROM car_recall
        )
        GROUP BY YEAR(recall_start_date)
        ORDER BY 년도
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.set_index("년도")

# ================타이틀 용도 (현황)==================
def get_recent_recalls(limit=3):
    engine = get_engine()

    query = text("""
        SELECT
            m.name AS 제조사,
            cm.name AS 차명,
            CASE
                WHEN CHAR_LENGTH(cr.recall_reason) > 20
                    THEN CONCAT(LEFT(cr.recall_reason, 20), '...')
                ELSE cr.recall_reason
            END AS 리콜사유
        FROM car_recall cr
        JOIN car_model cm ON cr.car_model_id = cm.id
        JOIN manufacturer m ON cm.manufacturer_id = m.id
        ORDER BY RAND()
        LIMIT :limit
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={"limit": limit}
        )

    return df

# =========== 뉴스 가져오기 ===========
def get_news(limit=3):
    engine = get_engine()

    query = text("""
        SELECT
            title,
            source,
            published_at AS date
        FROM news
        ORDER BY RAND()
        LIMIT :limit
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={"limit": limit}
        )

    return df.to_dict("records")

# ============== 검색 ==============
def search_recall(manufacturer=None, model=None, keyword=None):
    engine = get_engine()

    sql = """
    SELECT
        m.name AS 제작자,
        cm.name AS 차명,
        cr.production_start AS 생산기간_부터,
        cr.production_end AS 생산기간_까지,
        cr.recall_start_date AS 리콜개시일,
        cr.recall_count AS 리콜대수,
        cr.recall_reason AS 리콜사유
    FROM car_recall cr
    JOIN car_model cm
        ON cr.car_model_id = cm.id
    JOIN manufacturer m
        ON cm.manufacturer_id = m.id
    WHERE 1=1
    """

    params = {}

    if manufacturer and manufacturer != "전체":
        sql += " AND m.name LIKE :manufacturer"
        params["manufacturer"] = f"%{manufacturer}%"

    if model:
        sql += " AND cm.name LIKE :model"
        params["model"] = f"%{model}%"

    if keyword:
        sql += " AND cr.recall_reason LIKE :keyword"
        params["keyword"] = f"%{keyword}%"

    sql += " ORDER BY cr.recall_start_date DESC"

    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)