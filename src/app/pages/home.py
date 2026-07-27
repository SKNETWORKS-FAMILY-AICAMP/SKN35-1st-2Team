# import streamlit as st


# st.title("🚀 Test")


# st.write("메인 화면입니다.")



import streamlit as st

# 1. 페이지 기본 설정

st.set_page_config(
    page_title="차모아 - 자동차 리콜 & 서비스센터",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 사이드바

with st.sidebar:
    st.title("🚗 차모아 (CarMoa)")
    st.caption("스마트한 내 차 관리 통합 플랫폼")
    st.markdown("---")
    st.info(
        "💡 **Tip:** 차량 번호를 등록하시면 맞춤형 리콜 알림을 받아보실 수 있습니다."
    )

# 3. Hero 섹션

st.title("🚗 안전한 드라이빙의 시작, 차모아")
st.subheader("내 차의 리콜 소식부터 가까운 서비스센터 예약까지 한눈에 확인하세요.")
st.markdown("---")

# 4. 핵심 대시보드 지표

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="올해 진행된 리콜 건수", value="1,248 건", delta="전월 대비 +12%")
with col2:
    st.metric(
        label="최근 리콜 대상 차량 수",
        value="452,100 대",
        delta="-5%",
        delta_color="inverse",
    )
with col3:
    st.metric(label="오늘의 자동차 주요 뉴스", value="18 건", delta="새 소식 3건")
with col4:
    st.metric(label="제휴 서비스센터 수", value="3,820 곳", delta="전국 커버")

st.markdown("---")

# 5. 빠른 리콜 검색

st.markdown("### 🔍 빠른 리콜 검색")
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    car_model = st.text_input(
        "차종 또는 차량 번호를 입력하세요 (예: 쏘나타, 12삼 4567)",
        placeholder="차종명을 입력해 주세요...",
    )
with search_col2:
    st.write(" ")
    st.write(" ")
    if st.button("조회하기", use_container_width=True):
        st.success(f"'{car_model}' 검색 결과로 이동합니다.")

st.markdown("<br>", unsafe_allow_html=True)

# 6. 3개 핵심 영역 카드

col_recall, col_news, col_center = st.columns(3)

with col_recall:
    st.markdown("### 🚨 최근 대형 리콜 현황")
    with st.container(border=True):
        st.markdown("**현대자동차** | 아이오닉 5 / 6")
        st.caption("사유: ICCU(통합충전제어장치) 소프트웨어 오류")
        st.markdown("**기아** | EV6")
        st.caption("사유: LDC(저전압 덕트) 관련 교체")
        st.markdown("**BMW** | 520i / 530i")
        st.caption("사유: 스타터 모터 관련 소프트웨어 업데이트")
        if st.button("리콜 통계 및 상세 분석 보기 ➔", key="btn_recall"):
            st.write("리콜 분석 페이지로 이동합니다.")

with col_news:
    st.markdown("### 📰 실시간 자동차 뉴스")
    with st.container(border=True):
        st.markdown("📌 **[단독] 국토부, 전기차 배터리 안전 기준 대폭 강화**")
        st.caption("2시간 전 · 오토타임즈")
        st.markdown("📌 **내 주위 가장 저렴한 정비소 찾는 꿀팁 3가지**")
        st.caption("5시간 전 · 모터그래프")
        st.markdown("📌 **수입차 브랜드, 하반기 무상점검 캠페인 실시**")
        st.caption("1일 전 · 카이즈유")
        if st.button("자동차 뉴스 더보기 ➔", key="btn_news"):
            st.write("뉴스 페이지로 이동합니다.")

with col_center:
    st.markdown("### 📍 내 근처 서비스센터")
    with st.container(border=True):
        st.markdown("🛠️ **블루핸즈 역삼점** (0.8km)")
        st.caption("서울 강남구 테헤란로 | ⭐️ 4.8 (리뷰 120)")
        st.markdown("🛠️ **오토큐 서초점** (1.5km)")
        st.caption("서울 서초구 반포대로 | ⭐️ 4.7 (리뷰 98)")
        st.markdown("🛠️ **BMW 공식 서비스센터 대치** (2.3km)")
        st.caption("서울 강남구 영동대로 | ⭐️ 4.9 (리뷰 210)")
        if st.button("내 주변 서비스센터 검색 ➔", key="btn_center"):
            st.write("서비스센터 찾기 페이지로 이동합니다.")

# 7. 하단 안내 문구

st.markdown("---")
st.caption(
    "© 2026 CarMoa Inc. 본 서비스에서 제공하는 리콜 정보는 공공데이터포털 및 국토교통부 데이터를 기반으로 제작되었습니다."
)