import os
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT / "crawled" / "hyundai_service_centers.csv"

df = pd.read_csv(CSV_PATH)

load_dotenv()

KAKAO_JS_KEY = os.getenv("KAKAO_JS_KEY")

st.set_page_config(page_title="서비스 센터", layout="wide")

st.title("🗺️ 서비스 센터")

col1, col2, col3 = st.columns(3)

with col1:
    city = st.selectbox("시", ["서울시", "대전시", "광주시", "부산시", "제주시"])

with col2:
    district = st.selectbox("구", ["서초구", "종로구", "강서구", "강남구", "동대문구"])

with col3:
    company = st.selectbox("업체", ["현대", "기아", "벤츠", "BMW", "아우디"])

search_keyword = f"{company} 서비스센터 {city} {district}"

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}&libraries=services"></script>

</head>

<body style="margin:0">

<div id="map" style="width:100%;height:600px;"></div>

<script>

var container = document.getElementById("map");

var map = new kakao.maps.Map(container, {{
    center: new kakao.maps.LatLng(37.5665,126.9780),
    level:5
}});

var ps = new kakao.maps.services.Places();

ps.keywordSearch("{search_keyword}", placesSearchCB);

function placesSearchCB(data, status) {{

    if(status !== kakao.maps.services.Status.OK){{
        return;
    }}

    var bounds = new kakao.maps.LatLngBounds();

    for(var i=0;i<data.length;i++){{

        var marker = new kakao.maps.Marker({{
            map: map,
            position: new kakao.maps.LatLng(data[i].y, data[i].x)
        }});

        var infowindow = new kakao.maps.InfoWindow({{
            content:
            "<div style='padding:8px;width:220px;'>"
            + "<b>"+data[i].place_name+"</b><br>"
            + data[i].road_address_name
            + "</div>"
        }});

        kakao.maps.event.addListener(marker,'click',(function(marker,infowindow){{
            return function(){{
                infowindow.open(map,marker);
            }}
        }})(marker,infowindow));

        bounds.extend(new kakao.maps.LatLng(data[i].y,data[i].x));
    }}

    map.setBounds(bounds);
}}

</script>

</body>
</html>
"""

components.html(html, height=620)
