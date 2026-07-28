import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# db 모듈을 import하기 위해 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(str(Path(__file__).resolve().parents[2]))

# 검색 함수만 import 해오기
from db.chart.refind_data import search_recall

# ==========================
# 브랜드 컬러 시스템 (service_center.py와 동일)
# ==========================
BRAND_COLORS = {
    "현대": {"main": "#00AAD2", "dark": "#00728C"},
    "기아": {"main": "#BB162B", "dark": "#8C0F20"},
    "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
    "BMW": {"main": "#0066B1", "dark": "#003D6B"},
    "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
}
DEFAULT_ACCENT = {"main": "#2563EB", "dark": "#1D4ED8"}

brand_name_dict = {
    "전체": "All Brands",
    "현대": "Hyundai",
    "기아": "Kia",
    "벤츠": "Mercedes-Benz",
    "BMW": "BMW",
    "폭스바겐": "Volkswagen",
}
# 검색 함수만 import 해오기
from db.chart.refind_data import search_recall

st.set_page_config(page_title="Search", layout="wide")

st.title("자동차 리콜·결함 정보 검색")
st.caption("차종 · 기업 · 결함 안전등급을 검색해보세요")
st.subheader("조건 검색")

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


# ==========================
# 페이지 기본 설정 및 세션 상태 초기화
# ==========================
st.set_page_config(page_title="Search", layout="wide")

if "applied_manufacturer" not in st.session_state:
    st.session_state["applied_manufacturer"] = "전체"

if "applied_model" not in st.session_state:
    st.session_state["applied_model"] = ""

if "applied_keyword" not in st.session_state:
    st.session_state["applied_keyword"] = ""

# 현재 확정/적용된 테마 색상 계산
applied_manufacturer = st.session_state["applied_manufacturer"]
brand_name = brand_name_dict.get(applied_manufacturer, applied_manufacturer)

_accent = BRAND_COLORS.get(applied_manufacturer, DEFAULT_ACCENT)
ACCENT = _accent["main"]
ACCENT_DARK = _accent["dark"]
ACCENT_SOFT = hex_to_rgba(ACCENT, 0.08)
ACCENT_SOFT_STRONG = hex_to_rgba(ACCENT, 0.16)

# ==========================
# Custom CSS (적용된 테마 기반, service_center.py와 동일한 디자인 토큰)
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

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--canvas);
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] input {{
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        box-shadow: none !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:hover {{
        border-color: var(--accent) !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }}

    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p {{
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        line-height: 1.15rem !important;
        letter-spacing: 0.01em;
        color: var(--ink-soft) !important;
        text-transform: uppercase;
    }}

    div[data-baseweb="popover"] ul[data-baseweb="menu"],
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: var(--surface) !important;
        border-color: var(--line) !important;
    }}

    li[data-baseweb="option"] {{
        background-color: var(--surface) !important;
        color: var(--ink) !important;
    }}

    li[data-baseweb="option"]:hover,
    li[data-baseweb="option"][aria-selected="true"] {{
        background-color: {ACCENT_SOFT} !important;
        color: var(--ink) !important;
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
        border-bottom: 1px solid #E7EAF0;
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
        color: #0F172A !important;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.03em;
    }}
    .main-header p {{
        color: #64748B !important;
        font-size: 0.94rem;
        margin: 0;
    }}
    .main-header .brand-chip {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        color: #FFFFFF !important;
        background: var(--accent);
        padding: 0.55rem 1.05rem;
        border-radius: 999px;
        white-space: nowrap;
        box-shadow: 0 6px 16px var(--accent-soft-strong);
        transition: all 0.25s ease;
    }}

    .field-label-spacer {{
        min-height: 1.15rem;
        margin-bottom: 0.4rem;
        font-size: 0.76rem;
        font-weight: 700;
        line-height: 1.15rem;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        visibility: hidden;
        user-select: none;
    }}

    /* ---------- 필터 패널 / 카드 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1px solid #E7EAF0 !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"] {{
        padding: 0 0.85rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"]:first-child {{
        padding-left: 0.1rem;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"]:last-child {{
        padding-right: 0.1rem;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"]:not(:last-child) {{
        border-right: 1px solid #E7EAF0;
    }}

    /* ---------- 버튼 ---------- */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {{
        width: 100% !important;
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border-radius: 9px;
        height: 2.7rem;
        font-weight: 700;
        font-size: 0.95rem;
        border: none !important;
        transition: all 0.15s ease-in-out;
        margin-top: 0;
        box-shadow: 0 4px 12px var(--accent-soft-strong);
        letter-spacing: -0.01em;
    }}
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {{
        background: var(--accent-dark) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px var(--accent-soft-strong);
    }}
    div.stButton > button:active,
    div[data-testid="stFormSubmitButton"] > button:active {{
        transform: translateY(0px);
    }}

    /* ---------- 결과 요약 바 ---------- */
    .result-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF !important;
        border: 1px solid #E7EAF0 !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 10px;
        padding: 0.85rem 1.2rem;
        margin-top: 1.0rem;
        margin-bottom: 1.1rem;
        font-size: 0.92rem;
        color: #0F172A !important;
    }}
    .result-bar .result-location {{
        color: #64748B !important;
    }}
    .result-bar .result-location b {{
        color: #0F172A !important;
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
        color: #64748B !important;
        margin-left: 0.15rem;
    }}

    /* ---------- 빈 상태 ---------- */
    .empty-state {{
        background: #FFFFFF !important;
        border: 1px dashed #E7EAF0 !important;
        border-radius: 14px;
        padding: 3rem 1.5rem;
        text-align: center;
        color: #64748B !important;
        font-size: 0.95rem;
    }}
    .empty-state .empty-icon {{
        font-size: 2rem;
        margin-bottom: 0.6rem;
    }}

    /* ---------- 요약 통계 카드 ---------- */
    .stat-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin: 0.2rem 0 1.4rem 0;
    }}
    .stat-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}
    .stat-label {{
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        color: var(--ink-soft);
        margin-bottom: 6px;
    }}
    .stat-value {{
        font-family: 'Manrope', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--ink);
        line-height: 1.2;
    }}
    .stat-sub {{
        font-size: 11.5px;
        font-weight: 600;
        color: var(--accent-dark);
        background: var(--accent-soft);
        display: inline-block;
        padding: 2px 8px;
        border-radius: 999px;
        margin-top: 6px;
    }}

    /* ---------- 리콜 카드 ---------- */
    .recall-card {{
        position: relative;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        transition: all 0.15s ease;
    }}
    .recall-card:hover {{
        border-color: #CBD5E1;
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.06);
        transform: translateY(-1px);
    }}
    .recall-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }}
    .recall-title-wrap {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .recall-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.01em;
    }}
    .brand-badge {{
        display: inline-block;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
    }}
    .recall-count-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        color: #d9534f;
        background: #fdecea;
        padding: 4px 10px;
        border-radius: 999px;
    }}
    .recall-info-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 12px;
    }}
    .recall-info-item .label {{
        font-size: 11.5px;
        color: #999999;
        margin-bottom: 2px;
    }}
    .recall-info-item .value {{
        font-size: 13.5px;
        font-weight: 600;
        color: var(--ink);
    }}
    .recall-reason-box {{
        background: var(--canvas);
        border-radius: 8px;
        padding: 10px 14px;
        display: flex;
        gap: 8px;
    }}
    .recall-reason-text {{
        font-size: 13px;
        line-height: 1.6;
        color: #444444;
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
        <div class="eyebrow">Recall &amp; Defect Database</div>
        <h1>자동차 리콜·결함 정보 검색</h1>
        <p>차종 · 기업 · 결함 안전등급을 검색해보세요.</p>
    </div>
    <div class="brand-chip">🔍 {brand_name}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================
# 1. 상단 필터 영역 (드롭다운 + 텍스트 입력 + 조회 버튼을 한 패널에 배치)
# st.form으로 감싸서 입력창에서 Enter를 눌러도 검색되도록 함
# ==========================
with st.container(border=True):
    with st.form("search_form"):
        col1, col2, col3, col4 = st.columns([1, 1, 1.4, 0.85])

        with col1:
            manufacturer_list = ["전체", "벤츠", "BMW", "폭스바겐", "현대", "기아"]
            manufacturer = st.selectbox("🏭 기업(브랜드)", manufacturer_list)

        with col2:
            model = st.text_input("🚗 차종", placeholder="검색")

        with col3:
            keyword = st.text_input(
                "⚠️ 결함 키워드", placeholder="예: 브레이크, 엔진, 에어백"
            )

        with col4:
            st.markdown(
                '<div class="field-label-spacer">검색</div>', unsafe_allow_html=True
            )
            search_clicked = st.form_submit_button(
                "🔍 검색", use_container_width=True
            )

# ==========================
# 데이터 처리 및 검색 버튼(또는 Enter) 눌렀을 때만 조건/컬러 변경 적용
# ==========================
if search_clicked:
    st.session_state["applied_manufacturer"] = manufacturer
    st.session_state["applied_model"] = model.strip()
    st.session_state["applied_keyword"] = keyword.strip()

    with st.spinner("검색 중..."):
        try:
            df = search_recall(
                manufacturer=manufacturer,
                model=model.strip(),
                keyword=keyword.strip(),
            )
            st.session_state["search_result"] = df
            st.session_state["search_error"] = None
            st.session_state["search_condition"] = {
                "manufacturer": manufacturer,
                "model": model.strip(),
                "keyword": keyword.strip(),
            }
        except Exception as e:
            st.session_state["search_result"] = None
            st.session_state["search_error"] = str(e)

    st.rerun()

# ==========================
# 2. 결과 요약 바 + 3. 결과 리스트
# ==========================
if st.session_state.get("search_error"):
    st.markdown(
        f"""
        <div class="result-bar" style="border-left-color:#d9534f !important;">
            <span class="result-location">검색 중 오류가 발생했습니다</span>
            <span class="result-count" style="color:#d9534f;">⚠️</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.error(st.session_state["search_error"])

elif st.session_state.get("search_result") is not None:
    df = st.session_state["search_result"]
    cond = st.session_state.get("search_condition", {})

    cond_manufacturer = cond.get("manufacturer", "-")
    cond_model = cond.get("model") or "전체"
    cond_keyword = cond.get("keyword") or "전체"

    st.markdown(
        f"""
        <div class="result-bar">
            <span class="result-location">
                브랜드: <b>{cond_manufacturer}</b> · 차종: <b>{cond_model}</b> · 키워드: <b>{cond_keyword}</b>
            </span>
            <span class="result-count">{len(df)}<span>건</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                해당 조건에 등록된 리콜·결함 검색 결과가 없습니다.<br>
                다른 브랜드나 키워드를 선택해보세요.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # ── 상단 요약 통계 카드 ──
        total_count = len(df)
        total_recall_qty = int(df["리콜대수"].sum()) if "리콜대수" in df.columns else 0
        brand_count = df["제작자"].nunique() if "제작자" in df.columns else 0
        latest_date = df["리콜개시일"].max() if "리콜개시일" in df.columns else "-"

        st.markdown(
            f"""
            <div class="stat-row">
                <div class="stat-card">
                    <div class="stat-label">검색된 리콜 건수</div>
                    <div class="stat-value">{total_count}건</div>
                    <div class="stat-sub">조건 일치</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">총 리콜 대상 차량</div>
                    <div class="stat-value">{total_recall_qty:,}대</div>
                    <div class="stat-sub">합계</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">관련 브랜드 수</div>
                    <div class="stat-value">{brand_count}개</div>
                    <div class="stat-sub">브랜드</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">가장 최근 리콜일</div>
                    <div class="stat-value" style="font-size:1.25rem;">{latest_date}</div>
                    <div class="stat-sub">최신순</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"#### 상세 리콜 목록 ({total_count}건)")

        for _, row in df.iterrows():
            brand = row.get("제작자", "-")
            colors = BRAND_COLORS.get(brand, DEFAULT_ACCENT)
            recall_count_display = (
                f"{int(row['리콜대수']):,}대" if pd.notna(row.get("리콜대수")) else "-"
            )
            st.markdown(
                f"""
                <div class="recall-card" style="border-left: 5px solid; border-image: linear-gradient(180deg, {colors['main']}, {colors['dark']}) 1;">
                    <div class="recall-card-header">
                        <div class="recall-title-wrap">
                            <span class="brand-badge" style="background: {colors['main']};">{brand}</span>
                            <span class="recall-title">{row.get('차명', '-')}</span>
                        </div>
                        <div class="recall-count-badge">{recall_count_display}</div>
                    </div>
                    <div class="recall-info-grid">
                        <div class="recall-info-item">
                            <div class="label">생산기간</div>
                            <div class="value">{row.get('생산기간_부터', '-')} ~ {row.get('생산기간_까지', '-')}</div>
                        </div>
                        <div class="recall-info-item">
                            <div class="label">리콜 개시일</div>
                            <div class="value">{row.get('리콜개시일', '-')}</div>
                        </div>
                    </div>
                    <div class="recall-reason-box">
                        <div class="recall-reason-text">{row.get('리콜사유', '-')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.download_button(
            label="CSV로 다운로드",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="recall_search_result.csv",
            mime="text/csv",
        )