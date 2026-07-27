import pandas as pd

from db.database import get_db_connection

ALL_LABEL = "전체"


def get_sido_list():
    conn = get_db_connection()

    sql = """
        SELECT DISTINCT sido_name
        FROM legal_dong
        WHERE sido_name IS NOT NULL
        ORDER BY sido_name
    """

    df = pd.read_sql(sql, conn)

    conn.close()

    # 맨 앞에 "전체"를 추가해서 전국 검색을 선택할 수 있게 함
    return [ALL_LABEL] + df["sido_name"].tolist()


def get_sigungu_list(sido):
    # 시/도가 아직 "전체"면 하위 시/군/구도 고를 필요가 없음
    if not sido or sido == ALL_LABEL:
        return [ALL_LABEL]

    conn = get_db_connection()

    sql = """
        SELECT DISTINCT sigungu_name
        FROM legal_dong
        WHERE sido_name = %s
            AND sigungu_name IS NOT NULL
        ORDER BY sigungu_name
    """

    df = pd.read_sql(sql, conn, params=(sido,))

    conn.close()

    sigungu_list = (
        df["sigungu_name"]
        .str.replace(r"([가-힣]+시)([가-힣]+구)", r"\1 \2", regex=True)
        .tolist()
    )

    # 맨 앞에 "전체"를 추가해서 해당 시/도 전체를 선택할 수 있게 함
    return [ALL_LABEL] + sigungu_list


def get_manufacturer_list():
    conn = get_db_connection()

    sql = """
        SELECT *
        FROM manufacturer
    """

    df = pd.read_sql(sql, conn)

    conn.close()

    return df["name"].tolist()


def get_service_centers(company, sido=None, sigungu=None):
    conn = get_db_connection()

    conditions = ["m.name = %s"]
    params = [company]

    # 시/도가 "전체"가 아닐 때만 조건 추가
    if sido and sido != ALL_LABEL:
        conditions.append("sc.address LIKE CONCAT(%s, '%%')")
        params.append(sido)

    # 시/군/구가 "전체"가 아닐 때만 조건 추가
    if sigungu and sigungu != ALL_LABEL:
        conditions.append("sc.address LIKE CONCAT('%%', %s, '%%')")
        params.append(sigungu)

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            sc.name,
            sc.address,
            sc.phone,
            sc.latitude,
            sc.longitude
        FROM service_center sc
        JOIN manufacturer m
            ON sc.manufacturer_id = m.id
        WHERE {where_clause}
        ORDER BY sc.name
    """

    df = pd.read_sql(
        sql,
        conn,
        params=tuple(params),
    )

    conn.close()

    return df
