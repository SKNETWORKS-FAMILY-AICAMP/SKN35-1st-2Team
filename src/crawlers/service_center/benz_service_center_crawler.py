# benz 서비스 센터 crawler

import time
from pathlib import Path

import pandas as pd
import requests

from src.services.phone_format import format_phone

LIST_API = "https://api.oneweb.mercedes-benz.com/dms-plus/v3/api/dealers/market"

DETAIL_API = "https://api.oneweb.mercedes-benz.com/dms-plus/v3/api/dealers/id"


HEADERS = {"x-apikey": "ce7d9916-6a3d-407a-b086-fea4cbae05f6"}


ROOT = Path(__file__).resolve().parents[2]

SAVE_PATH = ROOT / "crawled" / "benz_service_centers.csv"


def crawling_service_center():
    """
    벤츠 서비스센터 API 데이터 수집
    """

    outlet_ids = []

    page = 1

    while True:
        params = {
            "marketCode": "KR",
            "searchProfile": "0001_DLp-KR",
            "page": page,
            "size": 250,
            "includeFields": (
                "address.coordinates.latitude,"
                "address.coordinates.longitude,"
                "legalName,"
                "outletId"
            ),
            "localeLanguage": "true",
            "strictGeo": "true",
            "expand": "false",
            "includeApplicants": "true",
        }

        response = requests.get(
            LIST_API,
            headers=HEADERS,
            params=params,
        )

        response.raise_for_status()

        result = response.json()

        dealers = result.get("dealers", [])

        if not dealers:
            break

        for dealer in dealers:
            outlet_id = dealer.get("outletId")

            if outlet_id:
                outlet_ids.append(outlet_id)

        page_info = result.get("page", {})

        current_page = page_info.get("number")

        total_pages = page_info.get("totalPages")

        print(f"목록 페이지 {current_page}/{total_pages}")

        if current_page >= total_pages:
            break

        page += 1

    print(f"전체 outlet 개수 : {len(outlet_ids)}")

    service_centers = []

    for index, outlet_id in enumerate(outlet_ids, start=1):
        print(f"[{index}/{len(outlet_ids)}] {outlet_id}")

        detail = get_dealer_detail(outlet_id)

        if not detail:
            continue

        if not is_service_center(detail):
            print("  → 서비스센터 아님")

            continue

        service_centers.append(detail)

        time.sleep(0.1)

    return service_centers


def get_dealer_detail(outlet_id):
    """
    상세 정보 조회
    """

    params = {
        "dealerIds": outlet_id,
        "includeFields": "*",
        "localeLanguage": "true",
    }

    response = requests.get(
        DETAIL_API,
        headers=HEADERS,
        params=params,
    )

    response.raise_for_status()

    result = response.json()

    dealers = result.get("dealers", [])

    if not dealers:
        return None

    return dealers[0]


def is_service_center(data):
    """
    Repair & Maintenance 존재 여부 확인
    """

    for service in data.get("offeredServices", []):
        name = service.get("service", {}).get("name")

        if name == "Repair & Maintenance":
            return True

    return False


def get_service_phone(data):
    """
    서비스센터 전화번호 추출
    """

    for service in data.get("offeredServices", []):
        service_name = service.get("service", {}).get("name")

        if service_name == "Repair & Maintenance":
            phone = service.get("communication", {}).get("PHONE")

            if phone:
                return phone

    phone = data.get("generalCommunication", {}).get("PHONE")

    return phone


def clean_name(name):

    if not name:
        return None

    return (
        name.replace("전시장 & ", "")
        .replace("전시장 / ", "")
        .replace("전시장", "")
        .replace("SR & SC", "서비스센터")
        .replace(" SR", "")
        .replace(" SC", " 서비스센터")
        .strip()
    )


def get_service_name(data):

    brands = data.get("brands", [])

    if brands:
        business_name = brands[0].get("businessName")

        if business_name:
            return clean_name(business_name)

    return clean_name(data.get("nameAddition"))


def parse_service_center(raw_data):
    """
    API 원본 데이터 → CSV 저장 형태 변환
    """

    rows = []

    for data in raw_data:
        address = data.get("address", {})

        coordinates = address.get("coordinates", {})

        rows.append(
            {
                "name": get_service_name(data),
                "address": (
                    f"{address.get('city')} "
                    f"{address.get('street')} "
                    f"{address.get('streetNumber')}"
                ),
                "phone": format_phone(get_service_phone(data)),
                "latitude": coordinates.get("latitude"),
                "longitude": coordinates.get("longitude"),
                "company": "벤츠",
            }
        )

    return rows


def save_csv(data, file_path):

    df = pd.DataFrame(data)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",
    )


def check_csv_created(file_path):

    if file_path.exists():
        size = file_path.stat().st_size

        print(f"CSV 파일 생성 완료: {file_path}")

        print(f"파일 크기: {size:,} bytes")

        return True

    print("CSV 파일 생성 실패")

    return False


def main():

    raw_data = crawling_service_center()

    service_center_data = parse_service_center(raw_data)

    save_csv(service_center_data, SAVE_PATH)

    check_csv_created(SAVE_PATH)


if __name__ == "__main__":
    main()
