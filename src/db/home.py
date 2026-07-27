import pandas as pd

from db.database import get_db_connection


def get_service_center_count():
    conn = get_db_connection()

    sql = """
        SELECT COUNT(*) as count
        FROM service_center
    """

    df = pd.read_sql(sql, conn)

    conn.close()

    return int(df["count"].iloc[0])

    # 맨 앞에 "전체"를 추가해서 전국 검색을 선택할 수 있게 함
