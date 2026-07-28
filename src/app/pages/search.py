import streamlit as st
import sqlite3
import pandas as pd
import os

# db 모듈을 import하기 위해 프로젝트 루트 경로를 sys.path에 추가
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

st.set_page_config(page_title="Search", layout="wide")

# 검색 함수만 import 해오기
from db.chart.refind_data import search_recall

st.set_page_config(page_title="자동차 리콜 검색", layout="wide")
st.title("자동차 리콜·결함 정보 검색")
st.caption("차종 · 기업 · 결함 안전등급을 검색해보세요")

st.subheader("조건 검색")

with st.form("search_form"):
    col1, col2, col3, col4 = st.columns([1, 1, 1.4, 0.5])

    with col1:
        manufacturer_list = ["전체", "벤츠", "BMW", "폭스바겐", "현대", "기아"]
        manufacturer = st.selectbox("기업(브랜드)", manufacturer_list)
# ---------------------------
# 화면 구성
# ---------------------------

    with col2:
        model = st.text_input("차종", placeholder="검색")

    with col3:
        keyword = st.text_input("결함 키워드", placeholder="예: 브레이크, 엔진, 에어백")

    with col4:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        search_clicked = st.form_submit_button("검색", use_container_width=True, type="primary")

if search_clicked:
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

if st.session_state.get("search_error"):
    st.divider()
    st.error(f"검색 중 오류가 발생했습니다: {st.session_state['search_error']}")

elif st.session_state.get("search_result") is not None:
    df = st.session_state["search_result"]
    cond = st.session_state.get("search_condition", {})

    st.divider()

    st.caption(
        f"검색 조건 — 브랜드: **{cond.get('manufacturer', '-')}** · "
        f"차종: **{cond.get('model') or '전체'}** · "
        f"키워드: **{cond.get('keyword') or '전체'}**"
    )

    if df.empty:
        st.subheader("검색 결과 (0건)")
        st.warning("검색 결과가 없습니다.")
    else:
        # ── 공통 스타일 (요약 카드 + 리콜 카드) ──
        st.markdown(
            """
            <style>
                .stat-row {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 14px;
                    margin: 8px 0 24px 0;
                }
                .stat-card {
                    background: #ffffff;
                    border: 1px solid #ececec;
                    border-radius: 12px;
                    padding: 14px 18px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
                }
                .stat-label {
                    font-size: 13px;
                    color: #8a8a8a;
                    margin-bottom: 6px;
                }
                .stat-value {
                    font-size: 24px;
                    font-weight: 800;
                    color: #1a1a1a;
                    line-height: 1.2;
                }
                .stat-sub {
                    font-size: 11.5px;
                    color: #4a9d5f;
                    background: #eaf7ee;
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 999px;
                    margin-top: 6px;
                }
                .recall-card {
                    position: relative;
                    background: #ffffff;
                    border: 1px solid #ececec;
                    border-radius: 12px;
                    padding: 16px 20px;
                    margin-bottom: 12px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                }
                .recall-card-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 12px;
                }
                .recall-title-wrap {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .recall-title {
                    font-size: 17px;
                    font-weight: 700;
                    color: #1a1a1a;
                }
                .brand-badge {
                    display: inline-block;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 3px 10px;
                    border-radius: 999px;
                }
                .recall-count-badge {
                    font-size: 13px;
                    font-weight: 700;
                    color: #d9534f;
                    background: #fdecea;
                    padding: 4px 10px;
                    border-radius: 999px;
                }
                .recall-info-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin-bottom: 12px;
                }
                .recall-info-item .label {
                    font-size: 11.5px;
                    color: #999999;
                    margin-bottom: 2px;
                }
                .recall-info-item .value {
                    font-size: 13.5px;
                    font-weight: 600;
                    color: #1a1a1a;
                }
                .recall-reason-box {
                    background: #f8f9fb;
                    border-radius: 8px;
                    padding: 10px 14px;
                    display: flex;
                    gap: 8px;
                }
                .recall-reason-text {
                    font-size: 13px;
                    line-height: 1.6;
                    color: #444444;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # ── 브랜드별 포인트 컬러 (main/dark 2톤) ──
        BRAND_COLORS = {
            "현대": {"main": "#00AAD2", "dark": "#00728C"},
            "기아": {"main": "#BB162B", "dark": "#8C0F20"},
            "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
            "BMW": {"main": "#0066B1", "dark": "#003D6B"},
            "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
        }
        DEFAULT_BRAND_COLOR = {"main": "#7c7c7c", "dark": "#5a5a5a"}

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
                    <div class="stat-value" style="font-size:20px;">{latest_date}</div>
                    <div class="stat-sub">최신순</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"#### 상세 리콜 목록 ({total_count}건)")

        for _, row in df.iterrows():
            brand = row.get("제작자", "-")
            colors = BRAND_COLORS.get(brand, DEFAULT_BRAND_COLOR)
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