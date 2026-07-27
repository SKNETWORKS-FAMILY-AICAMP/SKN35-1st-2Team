# kakao map을 활용하여 주소 값을 통한 위도 및 경도 데이터 추가 함수

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
_HEADERS = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}


def _search_address(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"

    res = requests.get(
        url,
        headers=_HEADERS,
        params={"query": address},
        timeout=5,
    )

    res.raise_for_status()

    docs = res.json().get("documents", [])

    if docs:
        return docs[0]["y"], docs[0]["x"]

    return None, None


def _search_keyword(keyword):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    res = requests.get(
        url,
        headers=_HEADERS,
        params={"query": keyword},
        timeout=5,
    )

    res.raise_for_status()

    docs = res.json().get("documents", [])

    if docs:
        return docs[0]["y"], docs[0]["x"]

    return None, None


def get_coords(address=None, keyword=None, delay=0.2):
    """
    주소로 먼저 검색하고, 실패하면 키워드(장소명)로 재시도.
    """

    lat, lng = None, None

    if address:
        try:
            lat, lng = _search_address(address)

        except requests.RequestException as e:
            print(f"[geocoding] 주소 검색 실패: {address} / {e}")

    if lat is None and keyword:
        try:
            lat, lng = _search_keyword(keyword)

        except requests.RequestException as e:
            print(f"[geocoding] 키워드 검색 실패: {keyword} / {e}")

    if lat is None:
        print(f"[geocoding] 좌표 변환 실패: address={address}, keyword={keyword}")

    time.sleep(delay)

    return lat, lng


def enrich_with_coords(
    data_list,
    address_key="주소",
    name_key="센터명",
    lat_key="latitude",
    lng_key="longitude",
):
    """
    dict 리스트를 받아서 위도/경도 컬럼을 채워서 반환.
    이미 좌표가 있는 항목은 스킵.
    """

    total = len(data_list)

    success_count = 0
    fail_count = 0
    skip_count = 0

    print(f"[geocoding 시작] 총 {total}개")

    for idx, row in enumerate(data_list, start=1):
        # 이미 좌표가 존재하면 스킵
        if row.get(lat_key) and row.get(lng_key):
            skip_count += 1

            print(f"[{idx}/{total}] 스킵 - 좌표 존재")

            continue

        lat, lng = get_coords(
            address=row.get(address_key),
            keyword=row.get(name_key),
        )

        row[lat_key] = lat
        row[lng_key] = lng

        if lat and lng:
            success_count += 1
            status = "성공"

        else:
            fail_count += 1
            status = "실패"

        print(
            f"[{idx}/{total}] "
            f"{status} | "
            f"성공:{success_count} "
            f"실패:{fail_count} "
            f"스킵:{skip_count}"
        )

    print("\n[geocoding 완료]")
    print(f"총 데이터: {total}")
    print(f"성공: {success_count}")
    print(f"실패: {fail_count}")
    print(f"스킵: {skip_count}")

    return data_list
