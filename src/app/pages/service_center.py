import json
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

KAKAO_JS_KEY = os.getenv("KAKAO_JS_KEY")


st.set_page_config(page_title="서비스 센터", layout="wide")


st.title("🗺️ 현대자동차 서비스 센터")


# ==============================
# 테스트용 수집 데이터
# ==============================

data = [
    {
        "센터코드": "J1Z008",
        "센터명": "(유)팔복현대서비스",
        "센터종류": "종합블루핸즈",
        "주소": "전북특별자치도 전주시 덕진구 동곡로 25",
        "전화번호": "063 2119688",
        "위도": 35.854827,
        "경도": 127.093682,
        "전기차수리": "Y",
        "수소차수리": "Y",
    },
    {
        "센터코드": "L1M008",
        "센터명": "(유)평화점",
        "센터종류": "전문블루핸즈",
        "주소": "전남특별자치도 목포시 평화로107번길 5",
        "전화번호": "061 2848504",
        "위도": 34.798436,
        "경도": 126.437789,
        "전기차수리": "N",
        "수소차수리": "N",
    },
    {
        "센터코드": "J01K45",
        "센터명": "(유)현대자동차익산서비스",
        "센터종류": "종합블루핸즈",
        "주소": "전북특별자치도 익산시 서동로 491",
        "전화번호": "063 8377111",
        "위도": 35.944281,
        "경도": 127.001429,
        "전기차수리": "Y",
        "수소차수리": "Y",
    },
    {
        "센터코드": "B03S17",
        "센터명": "(자)신흥공업사",
        "센터종류": "종합블루핸즈",
        "주소": "강원특별자치도 원주시 강변로 577",
        "전화번호": "033 7423533",
        "위도": 37.354751,
        "경도": 127.951697,
        "전기차수리": "N",
        "수소차수리": "Y",
    },
    {
        "센터코드": "SEOUL001",
        "센터명": "관악 현대 서비스센터",
        "센터종류": "종합블루핸즈",
        "주소": "서울특별시 관악구 남부순환로 123",
        "전화번호": "02 1234567",
        "위도": 37.4821,
        "경도": 126.9516,
        "전기차수리": "Y",
        "수소차수리": "N",
    },
]


df = pd.DataFrame(data)


# ==============================
# 필터
# ==============================

col1, col2 = st.columns(2)


with col1:
    city = st.selectbox(
        "시", ["전체", "서울특별시", "전북특별자치도", "강원특별자치도"]
    )


with col2:
    district = st.selectbox("구/시", ["전체", "관악구", "전주시", "익산시", "원주시"])


# ==============================
# 버튼 클릭
# ==============================

if st.button("지도 검색"):
    result = df.copy()

    if city != "전체":
        result = result[result["주소"].str.contains(city)]

    if district != "전체":
        result = result[result["주소"].str.contains(district)]

    st.dataframe(result)

    locations = result[["센터명", "주소", "전화번호", "위도", "경도"]].to_dict(
        "records"
    )

    location_json = json.dumps(locations, ensure_ascii=False)

    html = f"""
    <!DOCTYPE html>
    <html>

    <head>

    <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}"></script>

    </head>


    <body>

    <div id="map"
    style="width:100%;height:600px;">
    </div>



    <script>


    var data = {location_json};


    var container =
        document.getElementById('map');


    var map =
        new kakao.maps.Map(
            container,
            {{
                center:
                new kakao.maps.LatLng(
                    37.5665,
                    126.9780
                ),
                level:7
            }}
        );



    var bounds =
        new kakao.maps.LatLngBounds();



    data.forEach(function(center){{



        var position =
            new kakao.maps.LatLng(
                center.위도,
                center.경도
            );



        var marker =
            new kakao.maps.Marker({{

                map:map,
                position:position

            }});



        var info =
        new kakao.maps.InfoWindow({{

            content:
            `
            <div style="
            padding:10px;
            width:220px">

            <b>${{center.센터명}}</b>
            <br>

            ${{center.주소}}

            <br>

            ☎ ${{center.전화번호}}

            </div>
            `

        }});



        kakao.maps.event.addListener(
            marker,
            "click",
            function(){{
                info.open(
                    map,
                    marker
                );
            }}
        );



        bounds.extend(position);


    }});



    if(data.length > 0){{
        map.setBounds(bounds);
    }}



    </script>


    </body>
    </html>
    """

    components.html(html, height=620)
