# kia 서비스 센터 crawler

from pathlib import Path

import pandas as pd
import requests

from src.services.geocoding import enrich_with_coords
from src.services.phone_format import format_phone

URL = "https://members.kia.com/kr/knet/searchAsaList.do"

HEADERS = {
    "Accept": "application/json, text/javascript, */*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://members.kia.com/kr/view/qnet/asn_prct/qnet_asn_prct_index.do",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
}

ROOT = Path(__file__).resolve().parents[3]
SAVE_PATH = ROOT / "crawled" / "kia_service_centers.csv"


def crawling_service_center(url, headers):
    """
    KIA 서비스센터 API 데이터 수집
    """
    page = 1
    service_data = []

    while True:
        payload = {
            "funcobj": "searchAsaList",
            "searchType": "",
            "searchTypeSub": "",
            "siDoCd": "",
            "siDoNm": "",
            "siGunGuCd": "",
            "siGunGuNm": "",
            "schText": "",
            "schTextType": "",
            "selectType": "all",
            "asnCd": "",
            "currpage": str(page),
            "pagesize": "100",
            "schTextTemp": "",
            "selectTypeTemp": "all",
            "siDoCdTemp": "",
            "siGunGuCdTemp": "",
        }

        response = requests.post(url, headers=headers, data=payload)

        response.raise_for_status()

        result = response.json()

        service_list = result.get("searchAsaList", [])

        if not service_list:
            break

        service_data.extend(service_list)

        print(f"{page} 페이지 수집 완료 : {len(service_list)}개")

        total_count = service_list[0]["totalCount"]

        if len(service_data) >= total_count:
            break

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
                "name": item.get("poiName"),
                "address": item.get("addr"),
                "phone": format_phone(item.get("telNo")),
                "company": "기아",
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

    kia_service_center_data = enrich_with_coords(
        service_center_data,
        address_key="address",
        name_key="name",
    )

    save_csv(kia_service_center_data, SAVE_PATH)

    check_csv_created(SAVE_PATH)


if __name__ == "__main__":
    main()
