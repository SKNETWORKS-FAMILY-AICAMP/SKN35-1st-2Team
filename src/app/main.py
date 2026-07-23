# -----------------실행 방법-----------------
#  uv run streamlit run src/app/main.py
# ------------------------------------------

import streamlit as st

st.set_page_config(
    page_title="Test",
    page_icon="🚀",
    layout="wide",
)

# -------------------- CSS --------------------
st.markdown(
    """
<style>
[data-testid="stSidebar"]{
    min-width:260px;
    max-width:260px;
}

.sidebar-title{
    text-align:center;
    font-size:28px;
    font-weight:bold;
    margin-bottom:30px;
}

.sidebar-footer{
    text-align:center;
    color:gray;
    font-size:14px;
    margin-top:60px;
    line-height:1.8;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- Page --------------------
home = st.Page("pages/home.py", title="Home", icon="🏠")

page1 = st.Page("pages/page1.py", title="Chart", icon="🚗")

page2 = st.Page("pages/page2.py", title="페이지2", icon="2️⃣")

page3 = st.Page("pages/page3.py", title="페이지3", icon="3️⃣")

pg = st.navigation([home, page1, page2, page3], position="hidden")

# -------------------- Sidebar --------------------
with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🚀 프로젝트 이름</div>', unsafe_allow_html=True
    )

    st.page_link("pages/home.py", label="Home", icon="🏠")
    st.page_link("pages/page1.py", label="Chart", icon="🚗")
    st.page_link("pages/page2.py", label="페이지2", icon="2️⃣")
    st.page_link("pages/page3.py", label="페이지3", icon="3️⃣")

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
