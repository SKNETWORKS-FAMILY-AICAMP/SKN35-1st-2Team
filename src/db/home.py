from db.database import get_db_connection


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
