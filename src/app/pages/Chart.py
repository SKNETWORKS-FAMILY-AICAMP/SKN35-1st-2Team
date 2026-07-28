import streamlit as st
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from db.refind_data import (
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
# ============== 브랜드 색상 ==============
BRAND_COLORS = {
    "현대": {"main": "#00AAD2", "dark": "#00728C"},
    "기아": {"main": "#BB162B", "dark": "#8C0F20"},
    "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
    "BMW": {"main": "#0066B1", "dark": "#003D6B"},
    "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
}

st.markdown(
    f"""
<div class="main-header">
    <div>
        <div class="eyebrow">Official Service Network</div>
        <h1>자동차 리콜 분석</h1>
        <p>제조사와 분석 항목을 선택하여 리콜 현황과 위험도 분석 결과를 확인하세요.</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
st.divider()

# ============== 기업 선택 ==============
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
                compare_text = "전년 동월 대비"

            else:
                prev = latest
                compare_text = "비교 없음"

            diff = latest - prev

            if diff > 0:
                trend = "📈 증가"
                delta_color = "red"
            elif diff < 0:
                trend = "📉 감소"
                delta_color = "blue"
            else:
                trend = "➡ 유지"
                delta_color = "off"

            with col:
                st.metric(
                    label=f"{company} ({chart_df.index[-1]})",
                    value=f"{latest:,}건",
                    delta=f"{compare_text} {diff:+,}건 ({trend})",
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