from db.database import get_db_connection

ALL_LABEL = "전체"


# 시/도 리스트 조회


def get_sido_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT DISTINCT sido_name
        FROM legal_dong
        WHERE sido_name IS NOT NULL
        ORDER BY sido_name
    """

    cursor.execute(sql)

    result = [row["sido_name"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return [ALL_LABEL] + result


# 시/군/구 리스트 조회


def get_sigungu_list(sido):
    # 시/도가 아직 "전체"면 하위 시/군/구도 고를 필요가 없음
    if not sido or sido == ALL_LABEL:
        return [ALL_LABEL]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT DISTINCT sigungu_name
        FROM legal_dong
        WHERE sido_name = %s
            AND sigungu_name IS NOT NULL
        ORDER BY sigungu_name
    """

    cursor.execute(sql, (sido,))

    sigungu_list = [row["sigungu_name"] for row in cursor.fetchall()]

    conn.close()
    cursor.close()

    # 맨 앞에 "전체"를 추가해서 해당 시/도 전체를 선택할 수 있게 함
    return [ALL_LABEL] + sigungu_list


# 제조사 리스트 조회


def get_manufacturer_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM manufacturer
    """

    cursor.execute(sql)

    result = cursor.fetchall()

    conn.close()
    cursor.close()

    return [row["name"] for row in result]


# 조건에 일치하는 서비스 센터 리스트 조회


def get_service_centers(company, sido=None, sigungu=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    cursor.execute(sql, tuple(params))

    result = cursor.fetchall()

    for row in result:
        row["latitude"] = float(row["latitude"]) if row["latitude"] else None
        row["longitude"] = float(row["longitude"]) if row["longitude"] else None

    conn.close()
    cursor.close()

    return result
