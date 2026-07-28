from db.database import get_db_connection
import pandas as pd
from sqlalchemy import text
from db.engine import get_engine

def get_service_center_count():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT COUNT(*) as count
        FROM service_center
    """

    cursor.execute(sql)
    result = cursor.fetchone()["count"]

    conn.close()

    return result

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

# ================타이틀 용도 (뉴스)==================

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