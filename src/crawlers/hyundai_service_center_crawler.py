from pathlib import Path

import pandas as pd
import requests

from src.services.phone_format import format_phone

URL = "https://www.hyundai.com/wsvc/kr/front/biz/serviceNetwork.list.do"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.hyundai.com/kr/ko/service-membership/service-network/service-network/service-reservation-search",
    "Origin": "https://www.hyundai.com",
    "X-Requested-With": "XMLHttpRequest",
}

ROOT = Path(__file__).resolve().parents[2]
SAVE_PATH = ROOT / "crawled" / "hyundai_service_centers.csv"


def crawling_service_center(url, headers):
    """
    현대 서비스센터 API 데이터 수집
    """
    page = 1
    service_data = []

    while True:
        payload = {
            "pageNo": page,
            "selectBoxCity": "",
            "searchWord": "",
            "snGubunListSearch": "",
            "selectBoxCitySearch": "",
            "selectBoxTownShipSearch": "",
            "asnCd": "",
        }

        response = requests.post(url, headers=headers, data=payload)

        response.raise_for_status()

        result = response.json()

        service_list = result["data"]["result"]

        if not service_list:
            break

        service_data.extend(service_list)

        page += 1

    return service_data


def parse_service_center(raw_data):
    """
    API 원본 데이터 → CSV 저장 형태 변환
    """
    rows = []

    for item in raw_data:
        rows.append(
            {
                "name": item.get("asnNm"),
                "address": item.get("pbzAdrSbc"),
                "phone": format_phone(item.get("repnTn")),
                "latitude": item.get("mapLaeVal"),
                "longitude": item.get("mapLoeVal"),
                "company": "현대",
            }
        )

    return rows


def save_csv(data, file_path):
    """
    CSV 파일 생성
    """
    df = pd.DataFrame(data)

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",
    )


def check_csv_created(file_path):
    """
    CSV 생성 여부 확인
    """
    if file_path.exists():
        size = file_path.stat().st_size

        print(f"CSV 파일 생성 완료: {file_path}")
        print(f"파일 크기: {size:,} bytes")

        return True

    print("CSV 파일 생성 실패")
    return False


def main():
    raw_data = crawling_service_center(URL, HEADERS)

    service_center_data = parse_service_center(raw_data)

    save_csv(service_center_data, SAVE_PATH)

    check_csv_created(SAVE_PATH)


if __name__ == "__main__":
    main()
