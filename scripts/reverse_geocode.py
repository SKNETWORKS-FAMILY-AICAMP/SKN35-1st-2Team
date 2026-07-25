# crawling 해온 데이터의 주소 값의 규격이 다 다름으로 kakao map을 활용하여 위도 및 경도 값을 통한 통일화된 주소 값으로 재설정

import os
import time

import mysql.connector
import requests
from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

HEADERS = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT")),
    )


def reverse_geocode(latitude: float, longitude: float):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"

    response = requests.get(
        url,
        headers=HEADERS,
        params={
            "x": longitude,
            "y": latitude,
        },
        timeout=10,
    )

    response.raise_for_status()

    documents = response.json()["documents"]

    if not documents:
        return None

    document = documents[0]

    # 도로명 주소 우선
    if document["road_address"] is not None:
        return document["road_address"]["address_name"]

    # 도로명 주소가 없으면 지번 주소
    if document["address"] is not None:
        return document["address"]["address_name"]

    return None


def update_addresses():
    conn = get_db_connection()

    select_cursor = conn.cursor(dictionary=True)
    update_cursor = conn.cursor()

    select_cursor.execute("""
        SELECT
            id,
            latitude,
            longitude
        FROM service_center
        WHERE latitude IS NOT NULL
            AND longitude IS NOT NULL
    """)

    rows = select_cursor.fetchall()

    print(f"총 {len(rows)}건 처리")

    success = 0
    fail = 0

    for row in rows:
        try:
            new_address = reverse_geocode(
                row["latitude"],
                row["longitude"],
            )

            if new_address is None:
                fail += 1
                continue

            update_cursor.execute(
                """
                UPDATE service_center
                SET address = %s
                WHERE id = %s
                """,
                (
                    new_address,
                    row["id"],
                ),
            )

            success += 1

            if success % 100 == 0:
                conn.commit()
                print(f"{success}건 완료")

            # 카카오 API 과도한 호출 방지
            time.sleep(0.1)

        except Exception as e:
            fail += 1
            print(f"ID {row['id']} 실패 : {e}")

    conn.commit()

    select_cursor.close()
    update_cursor.close()
    conn.close()

    print("=" * 40)
    print(f"성공 : {success}")
    print(f"실패 : {fail}")


if __name__ == "__main__":
    update_addresses()
