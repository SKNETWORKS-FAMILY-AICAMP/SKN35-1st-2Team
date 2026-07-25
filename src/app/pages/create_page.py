import streamlit as st
from db_utils import add_post, BRANDS, CATEGORIES

st.set_page_config(page_title="글쓰기", page_icon="✏️", layout="wide")

if st.button("← 목록으로 가기"):
    st.switch_page("pages/community.py")

st.title("✏️ 새 게시글 작성")

with st.form("write_form", clear_on_submit=True):
    title = st.text_input("제목 *")
    col1, col2, col3 = st.columns(3)
    with col1:
        brand = st.selectbox("브랜드", BRANDS)
    with col2:
        model = st.text_input("모델명 (예: 아반떼 CN7)")
    with col3:
        category = st.selectbox("카테고리", CATEGORIES)
    author = st.text_input("작성자 닉네임", value="익명")
    content = st.text_area(
        "내용 *", height=220,
        placeholder="리콜 경험, 증상, 정비소 대응, 궁금한 점 등을 자유롭게 적어주세요.",
    )

    submitted = st.form_submit_button("게시글 등록", type="primary", use_container_width=True)
    if submitted:
        if not title.strip() or not content.strip():
            st.error("제목과 내용은 필수 입력 항목입니다.")
        else:
            add_post(title.strip(), content.strip(), brand, model.strip(), category, author.strip() or "익명")
            st.success("게시글이 등록되었습니다!")
            st.switch_page("pages/community.py")