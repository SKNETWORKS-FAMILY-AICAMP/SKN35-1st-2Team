import json
import os

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from db.service_center.service_center import (
    get_service_centers,
    get_sido_list,
    get_sigungu_list,
)

load_dotenv()

KAKAO_JS_KEY = os.getenv("KAKAO_JS_KEY")

# ==========================
# 브랜드 컬러 시스템
# ==========================
BRAND_COLORS = {
    "현대": {"main": "#00AAD2", "dark": "#00728C"},
    "기아": {"main": "#BB162B", "dark": "#8C0F20"},
    "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
    "BMW": {"main": "#0066B1", "dark": "#003D6B"},
    "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
}
DEFAULT_ACCENT = {"main": "#2563EB", "dark": "#1D4ED8"}


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


# ==========================
# 페이지 기본 설정 및 세션 상태 초기화
# ==========================
st.set_page_config(
    page_title="서비스 센터",
    page_icon="🔧",
    layout="wide",
)

# [핵심 변경] 조회 버튼 누르기 전과 후의 제조사를 분리 관리
if "applied_company" not in st.session_state:
    st.session_state["applied_company"] = "현대"

if "applied_sido" not in st.session_state:
    st.session_state["applied_sido"] = "전체"

if "applied_sigungu" not in st.session_state:
    st.session_state["applied_sigungu"] = "전체"

# 현재 확정/적용된 테마 색상 계산
brand_name_dict = {
    "현대": "Hyundai",
    "기아": "Kia",
    "벤츠": "Mercedes-Benz",
    "BMW": "BMW",
    "폭스바겐": "Volkswagen",
}

brand_name = brand_name_dict[st.session_state["applied_company"]]

applied_company = st.session_state["applied_company"]
_accent = BRAND_COLORS.get(applied_company, DEFAULT_ACCENT)
ACCENT = _accent["main"]
ACCENT_DARK = _accent["dark"]
ACCENT_SOFT = hex_to_rgba(ACCENT, 0.08)
ACCENT_SOFT_STRONG = hex_to_rgba(ACCENT, 0.16)

# ==========================
# Custom CSS (적용된 테마 기반)
# ==========================
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        --accent: {ACCENT};
        --accent-dark: {ACCENT_DARK};
        --accent-soft: {ACCENT_SOFT};
        --accent-soft-strong: {ACCENT_SOFT_STRONG};
        --ink: #0F172A;
        --ink-soft: #64748B;
        --line: #E7EAF0;
        --surface: #FFFFFF;
        --canvas: #F6F8FB;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background: var(--canvas);
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1360px;
    }}

    /* ---------- 헤더 ---------- */
    .main-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.6rem;
        padding-bottom: 1.4rem;
        border-bottom: 1px solid var(--line);
    }}
    .main-header .eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 0.55rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .main-header .eyebrow::before {{
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 0 4px var(--accent-soft);
    }}
    .main-header h1 {{
        font-family: 'Manrope', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 800 !important;
        color: var(--ink);
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.03em;
    }}
    .main-header p {{
        color: var(--ink-soft);
        font-size: 0.94rem;
        margin: 0;
    }}
    .main-header .brand-chip {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        color: #fff;
        background: var(--accent);
        padding: 0.55rem 1.05rem;
        border-radius: 999px;
        white-space: nowrap;
        box-shadow: 0 6px 16px var(--accent-soft-strong);
        transition: all 0.25s ease;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background: var(--canvas) !important;
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        transition: border-color 0.15s ease;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: var(--accent) !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div {{
        background: transparent !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: var(--ink) !important;
        fill: var(--ink) !important;
        opacity: 1 !important;
    }}
    div[data-testid="stSelectbox"] label p {{
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background: var(--surface) !important;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] li {{
        color: var(--ink) !important;
        background: var(--surface) !important;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
        background: var(--accent-soft) !important;
    }}

    /* ---------- 필터 패널 / 카드 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface);
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    /* ---------- 조회 버튼 ---------- */
    div.stButton > button {{
        width: 100% !important;
        background: var(--accent);
        color: white;
        border-radius: 9px;
        height: 2.7rem;
        font-weight: 700;
        font-size: 0.95rem;
        border: none;
        transition: all 0.15s ease-in-out;
        margin-top: 1.75rem;
        box-shadow: 0 4px 12px var(--accent-soft-strong);
        letter-spacing: -0.01em;
    }}
    div.stButton > button:hover {{
        background: var(--accent-dark);
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px var(--accent-soft-strong);
    }}
    div.stButton > button:active {{
        transform: translateY(0px);
    }}

    /* ---------- 결과 요약 바 ---------- */
    .result-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--surface);
        border: 1px solid var(--line);
        border-left: 4px solid var(--accent);
        border-radius: 10px;
        padding: 0.85rem 1.2rem;
        margin-top: 1.0rem;
        margin-bottom: 1.1rem;
        font-size: 0.92rem;
        color: var(--ink);
    }}
    .result-bar .result-location {{
        color: var(--ink-soft);
    }}
    .result-bar .result-location b {{
        color: var(--ink);
        font-weight: 700;
    }}
    .result-bar .result-count {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--accent);
    }}
    .result-bar .result-count span {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--ink-soft);
        margin-left: 0.15rem;
    }}

    /* ---------- 빈 상태 ---------- */
    .empty-state {{
        background: var(--surface);
        border: 1px dashed var(--line);
        border-radius: 14px;
        padding: 3rem 1.5rem;
        text-align: center;
        color: var(--ink-soft);
        font-size: 0.95rem;
    }}
    .empty-state .empty-icon {{
        font-size: 2rem;
        margin-bottom: 0.6rem;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================
# 헤더 영역
# ==========================
st.markdown(
    f"""
<div class="main-header">
    <div>
        <div class="eyebrow">Official Service Network</div>
        <h1>Service Center</h1>
        <p>지역과 제조사를 선택하여 주변 공식 서비스센터 위치 및 상세 정보를 확인하세요.</p>
    </div>
    <div class="brand-chip">🔧 {brand_name} Service Center</div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================
# 지도 렌더링 함수
# ==========================
def render_map(df, accent, accent_dark):
    locations = df.rename(
        columns={
            "name": "센터명",
            "address": "주소",
            "phone": "전화번호",
            "latitude": "위도",
            "longitude": "경도",
        }
    ).to_dict("records")

    location_json = json.dumps(locations, ensure_ascii=False)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    body {{
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #map {{
        width: 100%;
        height: 580px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        border: 1px solid #E7EAF0;
    }}

    .info-card {{
        padding: 14px 16px;
        width: 226px;
        font-size: 13px;
        line-height: 1.45;
        color: #1E293B;
        border-top: 3px solid {accent};
        border-radius: 2px;
    }}
    .info-title {{
        font-size: 14px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }}
    .info-addr {{
        color: #64748B;
        margin-bottom: 10px;
        word-break: keep-all;
        font-size: 12px;
    }}
    .info-phone {{
        display: inline-block;
        color: {accent_dark};
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        text-decoration: none;
        background: {hex_to_rgba(accent, 0.1)};
        padding: 5px 9px;
        border-radius: 5px;
        font-size: 12px;
    }}
</style>
<script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}"></script>
</head>
<body>

<div id="map"></div>

<script>
var data = {location_json};
var accentColor = "{accent}";

var container = document.getElementById("map");
var options = {{
    center: new kakao.maps.LatLng(36.5, 127.8),
    level: 12
}};

var map = new kakao.maps.Map(container, options);

var bounds = new kakao.maps.LatLngBounds();
var activeInfoWindow = null;
var validMarkerCount = 0;

var markerImage = new kakao.maps.MarkerImage(
    "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">' +
        '<path d="M17 0C7.6 0 0 7.6 0 17c0 12.7 17 25 17 25s17-12.3 17-25C34 7.6 26.4 0 17 0z" fill="' + accentColor + '"/>' +
        '<circle cx="17" cy="17" r="7" fill="#fff"/>' +
        '</svg>'
    ),
    new kakao.maps.Size(34, 42),
    {{ offset: new kakao.maps.Point(17, 42) }}
);

data.forEach(function(center) {{
    // 숫자형 좌표 체크 및 한국 영역 내 범위 체크 (위도 33~39, 경도 124~132)
    var lat = parseFloat(center.위도);
    var lng = parseFloat(center.경도);

    if (isNaN(lat) || isNaN(lng) || lat < 33 || lat > 39 || lng < 124 || lng > 132) {{
        return;
    }}

    var position = new kakao.maps.LatLng(lat, lng);

    var marker = new kakao.maps.Marker({{
        map: map,
        position: position,
        image: markerImage
    }});

    var content = `
        <div class="info-card">
            <div class="info-title">${{center.센터명}}</div>
            <div class="info-addr">${{center.주소}}</div>
            <a href="tel:${{center.전화번호}}" class="info-phone">📞 ${{center.전화번호}}</a>
        </div>
    `;

    var info = new kakao.maps.InfoWindow({{
        content: content,
        removable: true
    }});

    kakao.maps.event.addListener(marker, "click", function() {{
        if (activeInfoWindow) {{
            activeInfoWindow.close();
        }}
        info.open(map, marker);
        activeInfoWindow = info;
    }});

    bounds.extend(position);
    validMarkerCount++;
}});

// 데이터 이동 및 줌 영역 재설정
if (validMarkerCount > 0) {{
    // 마커가 1개인 경우 해당 마커 위치로 이동 후 레벨 조정
    if (validMarkerCount === 1) {{
        map.setCenter(bounds.getSouthWest());
        map.setLevel(4);
    }} else {{
        map.setBounds(bounds);
    }}
}}

// Iframe 로딩 및 setBounds 이후 지도가 깨지지 않도록 relayout만 호출
map.relayout();
</script>

</body>
</html>
"""
    components.html(html, height=590)


# ==========================
# 오른쪽 리스트 렌더링 함수
# ==========================
def render_list(df, accent, accent_dark):
    cards = ""
    for idx, row in df.iterrows():
        name = row.get("name", "센터명 없음")
        address = row.get("address", "주소 정보 없음")
        phone = row.get("phone", "전화번호 없음")

        kakao_search_url = f"https://map.kakao.com/link/search/{address} {name}"

        cards += f"""
        <div class="center-card">
            <div class="card-index">{idx + 1:02d}</div>
            <div class="card-body">
                <div class="card-header">
                    <span class="center-name">{name}</span>
                </div>
                <div class="center-address">📍 {address}</div>

                <div class="card-actions">
                    <a href="tel:{phone}" class="btn-phone">📞 {phone}</a>
                    <a href="{kakao_search_url}" target="_blank" class="btn-map">🧭 길찾기</a>
                </div>
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>
    body {{
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .center-list-container {{
        height: 580px;
        overflow-y: auto;
        padding-right: 6px;
        box-sizing: border-box;
    }}
    .center-card {{
        display: flex;
        gap: 12px;
        background-color: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-left: 3px solid {accent};
        border-radius: 12px;
        padding: 15px 16px;
        margin-bottom: 11px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        transition: all 0.15s ease;
    }}
    .center-card:hover {{
        border-color: #CBD5E1;
        border-left-color: {accent};
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.06);
        transform: translateY(-1px);
    }}
    .card-index {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        color: {accent_dark};
        background: {hex_to_rgba(accent, 0.1)};
        border-radius: 6px;
        min-width: 28px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .card-body {{
        flex: 1;
        min-width: 0;
    }}
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }}
    .center-name {{
        font-size: 1.0rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.01em;
    }}
    .center-address {{
        font-size: 0.83rem;
        color: #64748B;
        margin-bottom: 12px;
        line-height: 1.45;
    }}
    .card-actions {{
        display: flex;
        gap: 8px;
    }}
    .btn-phone {{
        flex: 1;
        text-align: center;
        font-size: 0.81rem;
        font-weight: 600;
        color: {accent_dark};
        background-color: {hex_to_rgba(accent, 0.08)};
        padding: 8px 0;
        border-radius: 7px;
        text-decoration: none;
        transition: background-color 0.15s ease;
    }}
    .btn-map {{
        flex: 1;
        text-align: center;
        font-size: 0.81rem;
        font-weight: 600;
        color: #475569;
        background-color: #F8FAFC;
        border: 1px solid #E7EAF0;
        padding: 8px 0;
        border-radius: 7px;
        text-decoration: none;
        transition: background-color 0.15s ease;
    }}
    .btn-phone:hover {{ background-color: {hex_to_rgba(accent, 0.16)}; }}
    .btn-map:hover {{ background-color: #F1F5F9; color: #1E293B; }}

    .center-list-container::-webkit-scrollbar {{ width: 5px; }}
    .center-list-container::-webkit-scrollbar-thumb {{
        background-color: #E2E8F0;
        border-radius: 3px;
    }}
</style>
</head>
<body>
    <div class="center-list-container">
        {cards}
    </div>
</body>
</html>
"""
    components.html(html, height=590)


# ==========================
# 1. 상단 필터 영역 (드롭다운 3개 + 조회 버튼)
# ==========================
filter_col, btn_col = st.columns([3, 1])

with filter_col, st.container(border=True):
    col_sido, col_sigungu, col_company = st.columns([1, 1, 1])

    with col_sido:
        raw_sido = get_sido_list()
        sido_list = list(dict.fromkeys(["전체"] + raw_sido))
        selected_sido = st.selectbox("📍 시 / 도", sido_list)

    with col_sigungu:
        if selected_sido == "전체":
            sigungu_list = ["전체"]
        else:
            raw_sigungu = get_sigungu_list(selected_sido)
            sigungu_list = list(dict.fromkeys(["전체"] + raw_sigungu))

        selected_sigungu = st.selectbox(
            "🏙️ 시 / 군 / 구",
            sigungu_list,
            disabled=(selected_sido == "전체"),
        )

    with col_company:
        # [핵심 변경] 드롭다운 선택값만 저장 (아직 적용 안됨)
        brand_keys = list(BRAND_COLORS.keys())
        default_index = (
            brand_keys.index(applied_company) if applied_company in brand_keys else 0
        )
        selected_company = st.selectbox("🏭 제조사", brand_keys, index=default_index)

with btn_col, st.container(border=True):
    search_clicked = st.button("🔍 조회하기", use_container_width=True)


# ==========================
# 데이터 처리 및 조회 버튼 눌렀을 때만 조건/컬러 변경 적용
# ==========================
# [핵심 변경] 조회 버튼 클릭 시 세션 상태를 갱신하고 페이지 새로고침
if search_clicked:
    st.session_state["applied_company"] = selected_company
    st.session_state["applied_sido"] = selected_sido
    st.session_state["applied_sigungu"] = selected_sigungu
    st.session_state["map_result"] = get_service_centers(
        company=selected_company,
        sido=selected_sido,
        sigungu=selected_sigungu,
    )
    # 색상 반영을 위해 리런
    st.rerun()

# 최초 실행 시 데이터 로드
if "map_result" not in st.session_state:
    st.session_state["map_result"] = get_service_centers(
        company=st.session_state["applied_company"],
        sido=st.session_state["applied_sido"],
        sigungu=st.session_state["applied_sigungu"],
    )

df = st.session_state["map_result"]

# 라벨에 적용된 상태 반영
app_sido = st.session_state["applied_sido"]
app_sigungu = st.session_state["applied_sigungu"]

if app_sido == "전체":
    location_label = "전국"
elif app_sigungu == "전체":
    location_label = app_sido
else:
    location_label = f"{app_sido} {app_sigungu}"


# ==========================
# 2. 결과 요약 바 (전체 너비로 중간 배치)
# ==========================
st.markdown(
    f"""
    <div class="result-bar">
        <span class="result-location"><b>{location_label}</b> · <b>{applied_company}</b> 서비스센터 검색 결과</span>
        <span class="result-count">{len(df)}<span>곳</span></span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================
# 3. 지도 및 데이터 리스트 영역 (결과 바 하단 배치)
# ==========================
if df.empty:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">🗺️</div>
            해당 조건에 등록된 서비스센터 검색 결과가 없습니다.<br>
            다른 지역이나 제조사를 선택해보세요.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    map_col, list_col = st.columns([2, 1])

    with map_col:
        render_map(df, ACCENT, ACCENT_DARK)

    with list_col:
        render_list(df, ACCENT, ACCENT_DARK)
