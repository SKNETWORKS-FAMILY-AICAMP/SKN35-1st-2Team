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
    margin-bottom:20px;
}

.sidebar-footer{
    text-align:center;
    color:gray;
    font-size:14px;
    margin-top:15px;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- Page --------------------
home = st.Page("streamlit/home.py", title="Home", icon="🏠")

page1 = st.Page("streamlit/page1.py", title="페이지1", icon="1️⃣")

page2 = st.Page("streamlit/page2.py", title="페이지2", icon="2️⃣")

page3 = st.Page("streamlit/page3.py", title="페이지3", icon="3️⃣")

pg = st.navigation([home, page1, page2, page3], position="hidden")

# -------------------- Sidebar --------------------
with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🚀 프로젝트 이름</div>', unsafe_allow_html=True
    )

    st.page_link("streamlit/home.py", label="Home", icon="🏠")
    st.page_link("streamlit/page1.py", label="페이지1", icon="1️⃣")
    st.page_link("streamlit/page2.py", label="페이지2", icon="2️⃣")
    st.page_link("streamlit/page3.py", label="페이지3", icon="3️⃣")

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
