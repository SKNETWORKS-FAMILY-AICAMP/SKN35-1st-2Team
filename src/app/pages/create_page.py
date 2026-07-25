import os
import sys
import streamlit as st

# src 및 루트 디렉토리를 sys.path 최상단에 추가
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from db.db_utils import add_post, BRANDS, CATEGORIES

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
    
    col_author, col_pw = st.columns(2)
    with col_author:
        author = st.text_input("작성자 닉네임", value="익명")
    with col_pw:
        password = st.text_input("비밀번호 (수정/삭제용) *", type="password", placeholder="수정 및 삭제 시 사용할 비밀번호")

    content = st.text_area(
        "내용 *", height=220,
        placeholder="리콜 경험, 증상, 정비소 대응, 궁금한 점 등을 자유롭게 적어주세요.",
    )

    submitted = st.form_submit_button("게시글 등록", type="primary", use_container_width=True)
    if submitted:
        if not title.strip() or not content.strip() or not password.strip():
            st.error("제목, 내용, 비밀번호는 필수 입력 항목입니다.")
        else:
            add_post(title.strip(), content.strip(), brand, model.strip(), category, author.strip() or "익명", password.strip())
            st.success("게시글이 등록되었습니다!")
            st.switch_page("pages/community.py")