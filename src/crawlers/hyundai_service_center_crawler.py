import pandas as pd
import requests

URL = "https://www.hyundai.com/wsvc/kr/front/biz/serviceNetwork.list.do"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.hyundai.com/kr/ko/service-membership/service-network/service-network/service-reservation-search",
    "Origin": "https://www.hyundai.com",
    "X-Requested-With": "XMLHttpRequest",
}

all_rows = []

page = 1

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

    response = requests.post(URL, headers=HEADERS, data=payload)

    response.raise_for_status()

    result = response.json()

    service_list = result["data"]["result"]

    if not service_list:
        break

    for item in service_list:
        all_rows.append(
            {
                "센터코드": item.get("asnCd"),
                "센터명": item.get("asnNm"),
                "센터종류": item.get("apimCeqPlntNm"),
                "주소": item.get("pbzAdrSbc"),
                "전화번호": item.get("repnTn"),
                "위도": item.get("mapLaeVal"),
                "경도": item.get("mapLoeVal"),
                "전기차수리": item.get("spcialSrvC001"),
                "수소차수리": item.get("spcialSrvH001"),
            }
        )

    page += 1

df = pd.DataFrame(all_rows)

df.to_csv(
    "../crawled/hyundai_service_centers.csv",
    index=False,
    encoding="utf-8-sig",
)
