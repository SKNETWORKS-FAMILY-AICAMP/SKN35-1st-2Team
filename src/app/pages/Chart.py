import streamlit as st
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.db.chart.refind_data import (
    get_company_list,
    get_year_range,
    get_yearly_recall,
    get_car_model_recall,
    get_risk_trend,
)

st.set_page_config(
    page_title="Chart",
    layout="wide",
)

# ============== 브랜드 색상 (service_center.py와 동일) ==============
BRAND_COLORS = {
    "현대": {"main": "#00AAD2", "dark": "#00728C"},
    "기아": {"main": "#BB162B", "dark": "#8C0F20"},
    "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
    "BMW": {"main": "#0066B1", "dark": "#003D6B"},
    "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
}
DEFAULT_ACCENT = {"main": "#2563EB", "dark": "#1D4ED8"}

# 이 페이지는 여러 기업을 동시에 비교하는 페이지라 특정 브랜드 하나로 고정된
# 테마를 쓰지 않고, 공통 기본 액센트 컬러(DEFAULT_ACCENT)를 사용
ACCENT = DEFAULT_ACCENT["main"]
ACCENT_DARK = DEFAULT_ACCENT["dark"]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


ACCENT_SOFT = hex_to_rgba(ACCENT, 0.08)
ACCENT_SOFT_STRONG = hex_to_rgba(ACCENT, 0.16)

# ==========================
# Custom CSS (service_center.py와 동일한 디자인 토큰)
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
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        box-shadow: none !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"]:hover {{
        border-color: var(--accent) !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] * {{
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }}

    div[data-testid="stSelectbox"] label p,
    div[data-testid="stMultiSelect"] label p {{
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        line-height: 1.15rem !important;
        letter-spacing: 0.01em;
        color: var(--ink-soft) !important;
        text-transform: uppercase;
    }}

    /* 멀티셀렉트에서 선택된 기업 태그(pill) 컬러 */
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
    }}

    /* 선택된 기업 이름 텍스트 색상 */
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {{
        color: #FFFFFF !important;
    }}

    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {{
        fill: #FFFFFF !important;
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

    /* 라디오 버튼(그래프 종류) 선택 컬러 */
    div[data-testid="stRadio"] label p {{
        color: var(--ink) !important;
    }}
    div[data-testid="stRadio"] input:checked + div {{
        background-color: var(--accent) !important;
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

    /* ---------- 필터 패널 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1px solid #E7EAF0 !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    /* ---------- Metric 카드 (위험도 탭) ---------- */
    div[data-testid="stMetricDelta"] svg {{
        display: none !important;
    }}

    div[data-testid="stMetricDelta"] {{
        font-weight: 700 !important;
    }}
    div[data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
        text-transform: uppercase;
        color: var(--ink-soft) !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Manrope', sans-serif;
        color: var(--ink) !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================
# 헤더 영역
# ==========================
st.markdown(
    """
<div class="main-header">
    <div>
        <div class="eyebrow">Recall Analytics</div>
        <h1>자동차 리콜 분석</h1>
        <p>제조사와 분석 항목을 선택하여 리콜 현황과 위험도 분석 결과를 확인하세요.</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============== 기업 선택 ==============
with st.container(border=True):
    companies = get_company_list()

    selected_companies = st.multiselect(
        "비교할 기업 선택",
        companies
    )

    # ============== 그래프 종류 ==============
    graph_options = ["년도별 리콜건수", "위험도"]

    if len(selected_companies) == 1:
        graph_options.insert(1, "차종별 리콜건수")

    graph_type = st.radio(
        "그래프 종류",
        graph_options,
        horizontal=True
    )

if not selected_companies:
    st.info("기업을 선택해주세요.")
    st.stop()


# ============== 연도 선택 ==============
if graph_type != "위험도":

    if selected_companies:
        min_year, max_year = get_year_range(selected_companies)

        # 데이터가 없는 경우 대비
        if min_year is None or max_year is None:
            min_year, max_year = 2012, 2024
    else:
        min_year, max_year = 2012, 2024

    years = list(range(min_year, max_year + 1))

    col1, col2 = st.columns(2)

    with col1:
        start = st.selectbox(
            "시작년도",
            years,
            index=0
        )

    with col2:
        end = st.selectbox(
            "종료년도",
            years,
            index=len(years) - 1
        )

st.divider()
# ==========================================================
# 년도별
# ==========================================================

if graph_type == "년도별 리콜건수":

    compare_df = pd.DataFrame()

    for company in selected_companies:

        df = get_yearly_recall(company, start, end)

        if df.empty:
            continue

        df = df.rename(columns={"리콜건수": company})

        if compare_df.empty:
            compare_df = df
        else:
            compare_df = compare_df.join(df, how="outer")

    compare_df = compare_df.fillna(0)

    if compare_df.empty:
        st.warning("조회된 데이터가 없습니다.")
    else:

        plot_df = compare_df.reset_index().melt(
            id_vars="년도",
            var_name="기업",
            value_name="리콜건수"
        )

        plot_df["년도"] = plot_df["년도"].astype(str) + "년"

        fig = px.line(
            plot_df,
            x="년도",
            y="리콜건수",
            color="기업",
            markers=True,
            color_discrete_map={
                c: BRAND_COLORS[c]["main"]
                for c in selected_companies
                if c in BRAND_COLORS
            }
        )

        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 차종별
# ==========================================================

elif graph_type == "차종별 리콜건수":

    compare_df = pd.DataFrame()

    for company in selected_companies:

        df = get_car_model_recall(company, start, end)

        if df.empty:
            continue

        df = df.rename(columns={"리콜건수": company})

        if compare_df.empty:
            compare_df = df
        else:
            compare_df = compare_df.join(df, how="outer")

    compare_df = compare_df.fillna(0)

    if compare_df.empty:
        st.warning("조회된 데이터가 없습니다.")
    else:

        plot_df = compare_df.reset_index().melt(
            id_vars="차명",
            var_name="기업",
            value_name="리콜건수"
        )

        fig = px.bar(
            plot_df,
            x="차명",
            y="리콜건수",
            color="기업",
            barmode="group",
            color_discrete_map={
                c: BRAND_COLORS[c]["main"]
                for c in selected_companies
                if c in BRAND_COLORS
            }
        )

        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 위험도
# ==========================================================

elif graph_type == "위험도":

    compare_df = pd.DataFrame()
    risk_data = {}

    for company in selected_companies:

        df = get_risk_trend(company)

        if df.empty:
            continue

        risk_data[company] = df.copy()

        df = df.rename(columns={"리콜건수": company})

        if compare_df.empty:
            compare_df = df
        else:
            compare_df = compare_df.join(df, how="outer")

    compare_df = compare_df.fillna(0)

    if compare_df.empty:
        st.warning("최근 2년 데이터가 없습니다.")

    else:

        # ==========================================
        # Metric
        # ==========================================
        cols = st.columns(len(risk_data))

        for col, (company, chart_df) in zip(cols, risk_data.items()):

            latest = chart_df["리콜건수"].iloc[-1]

            if len(chart_df) >= 13:
                prev = chart_df["리콜건수"].iloc[-13]
                compare_text = "전년 대비"

            else:
                prev = latest
                compare_text = "비교 없음"

            diff = latest - prev

            if diff > 0:
                trend = "↑ 증가"
                delta_color = "red"

            elif diff < 0:
                trend = "↓ 감소"
                delta_color = "blue"

            else:
                trend = "→ 유지"
                delta_color = "off"

            with col:
                st.metric(
                    label=f"{company} ({chart_df.index[-1]})",
                    value=f"{latest:,}건",
                    delta=f"{trend} {compare_text} {diff:+,}건",
                    delta_color=delta_color
                )

        st.divider()

        # ==========================================
        # 그래프
        # ==========================================

        plot_df = compare_df.reset_index()

        plot_df = plot_df.rename(columns={"index": "연월"})

        plot_df = plot_df.melt(
            id_vars="연월",
            var_name="기업",
            value_name="리콜건수"
        )

        plot_df["연월"] = pd.to_datetime(plot_df["연월"])

        fig = px.line(
            plot_df,
            x="연월",
            y="리콜건수",
            color="기업",
            markers=True,
            color_discrete_map={
                c: BRAND_COLORS[c]["main"]
                for c in selected_companies
                if c in BRAND_COLORS
            }
        )

        fig.update_layout(
            xaxis_title="연월",
            yaxis_title="리콜 건수",
            legend_title="기업"
        )

        st.plotly_chart(fig, use_container_width=True)
