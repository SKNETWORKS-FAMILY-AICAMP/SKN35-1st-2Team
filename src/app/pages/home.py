import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from db.refind_data import (
    get_latest_trend,
    get_recent_recalls
)

trend_df = get_latest_trend()
recent_df = get_recent_recalls()

latest = trend_df.iloc[-1]
prev = trend_df.iloc[-2]

recall_diff = latest["리콜건수"] - prev["리콜건수"]
vehicle_diff = latest["리콜대상차량수"] - prev["리콜대상차량수"]

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="차모아 - 자동차 리콜 & 서비스센터",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. Hero 섹션
st.title("🚗 안전한 드라이빙의 시작, 차모아")
st.subheader("우리 차, 지금 리콜 대상인지 3초 만에 확인하세요.")
st.markdown("---")

# 4. 핵심 대시보드 지표
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label=f"{trend_df.index[-1]}년 리콜 건수",
        value=f"{int(latest['리콜건수']):,}건",
        delta=f"{recall_diff:+,}건",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label=f"{trend_df.index[-1]}년 리콜 대상 차량 수",
        value=f"{int(latest['리콜대상차량수']):,}대",
        delta=f"{vehicle_diff:+,}대",
        delta_color="inverse"
    )
# 민하님 여기에 25년도 6월 이후의 뉴스들? 총 몇개 인지 가져오는 함수 해주시면 될 것 같아요
with col3:
    st.metric(label="25년 자동차 주요 뉴스", value="18 건", delta="새 소식 3건")
# 찬룡님 서비스 센터 몇 개 인지 가져오는 함수로 해주시면 될 것 같습니다
with col4:
    st.metric(label="제휴 서비스센터 수", value="3,820 곳", delta="전국 커버")

st.markdown("---")

# 5. 3개 핵심 영역 카드
col_recall, col_news, col_center = st.columns(3)

with col_recall:
    st.markdown("### 🚨 최근 리콜 현황")
    with st.container(border=True):
        for _, row in recent_df.iterrows():
            st.markdown(
                f"**{row['제조사']}** | {row['차명']}"
            )
            st.caption(f"사유: {row['리콜사유']}")

        if st.button("📈 리콜 분석 바로가기", key="btn_chart"):
            st.switch_page("pages/Chart.py")

with col_news:
    st.markdown("### 📰 25년 자동차 뉴스")
    with st.container(border=True):
        st.markdown("📌 **[단독] 국토부, 전기차 배터리 안전 기준 대폭 강화**")
        st.caption("2시간 전 · 오토타임즈")
        st.markdown("📌 **내 주위 가장 저렴한 정비소 찾는 꿀팁 3가지**")
        st.caption("5시간 전 · 모터그래프")
        st.markdown("📌 **수입차 브랜드, 하반기 무상점검 캠페인 실시**")
        st.caption("1일 전 · 카이즈유")
        if st.button("📰 자동차 뉴스 더보기", key="btn_news"):
            st.switch_page("pages/news.py")

with col_center:
    st.markdown("### 📍 내 근처 서비스센터")
    with st.container(border=True):
        st.markdown("🛠️ **블루핸즈 역삼점** (0.8km)")
        st.caption("서울 강남구 테헤란로 | ⭐️ 4.8 (리뷰 120)")
        st.markdown("🛠️ **오토큐 서초점** (1.5km)")
        st.caption("서울 서초구 반포대로 | ⭐️ 4.7 (리뷰 98)")
        st.markdown("🛠️ **BMW 공식 서비스센터 대치** (2.3km)")
        st.caption("서울 강남구 영동대로 | ⭐️ 4.9 (리뷰 210)")
        if st.button("🗺️ 내 주변 서비스센터 검색", key="btn_center"):
            st.switch_page("pages/service_center.py")

# 6. 하단 안내 문구
st.markdown("---")
st.caption(
    "© 2026 CarMoa Inc. 본 서비스에서 제공하는 리콜 정보는 공공데이터포털 및 국토교통부 데이터를 기반으로 제작되었습니다."
)