# -----------------실행 방법-----------------
#  uv run streamlit run src/app/main.py
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)  # ------------------------------------------

import os
import sys

# src 및 루트 디렉토리를 sys.path 최상단에 추가 (ModuleNotFoundError 예방)
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from db.db_utils import init_db

init_db()

# -------------------- CSS --------------------
# -------------------- CSS --------------------
st.markdown(
    """
<style>
/* 1. 사이드바 너비 지정 (강제 min-width 제거하여 슬라이딩 접힘 정상 동작) */
section[data-testid="stSidebar"] {
    width: 260px !important;
}
/* 2. 상단 헤더 위치 보정 (가려짐 방지) 및 본문 패딩 조정 */
header[data-testid="stHeader"] {
    z-index: 99;
.sidebar-title{
    text-align:center;
    font-size:26px;
    font-weight:bold;
    margin-bottom:30px;
}

/* 3. 본문 영역을 전체 화면 기준 중앙 정렬 및 반응형 여백 적용 */
.main .block-container {
    max-width: 1400px !important; /* 원하시는 본문 최대 너비 */
    width: 100% !important;
    margin: 0 auto !important;    /* 사이드바 여부에 따라 항상 반응형 중앙 정렬 */
    padding-top: 4rem !important;  /* 상단 헤더 아이콘에 제목이 가려지지 않게 여백 확보 */
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 사이드바 내부 커스텀 스타일 */
.sidebar-title {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 30px;
}

.sidebar-footer {
    text-align: center;
    color: gray;
    font-size: 14px;
    margin-top: 60px;
    line-height: 1.8;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- Page --------------------
home = st.Page("pages/home.py", title="Home", icon="🏠")

page1 = st.Page("pages/Chart.py", title="Chart", icon="📈")

page2 = st.Page("pages/search.py", title="Search", icon="🔍")

page3 = st.Page("pages/FAQ.py", title="FAQ", icon="❓")

page4 = st.Page("pages/news.py", title="소식", icon="📰")

page5 = st.Page("pages/service_center.py", title="서비스 센터", icon="🗺️")

page6 = st.Page("pages/community.py", title="소통공간", icon="💬")

page7 = st.Page("pages/create_page.py", title="글작성")

page8 = st.Page("pages/edit_page.py", title="글수정")

page9 = st.Page("pages/detail_page.py", title="게시글 상세")

pg = st.navigation([home, page1, page2, page3, page4, page5, page6, page7, page8, page9], position="hidden")

# -------------------- Sidebar --------------------
with st.sidebar:
    st.title("🚗 차모아 (CarMoa)")
    st.markdown("---")
    st.page_link("pages/home.py", label="Home", icon="🏠")
    st.page_link("pages/Chart.py", label="Chart", icon="📈")
    st.page_link("pages/search.py", label="Search", icon="🔍")
    st.page_link("pages/FAQ.py", label="FAQ", icon="❓")
    st.page_link("pages/news.py", label="News", icon="📰")
    st.page_link("pages/service_center.py", label="Service_Center", icon="🗺️")
    st.page_link("pages/community.py", label="Community", icon="💬")

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-footer">
            SKN35<br>
            1st 2Team<br>
            화이팅~
        </div>
        """,
        unsafe_allow_html=True,
    )

pg.run()
