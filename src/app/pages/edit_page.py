# 수정일자: 2026-07-26
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

from db.db_utils import get_post, update_post, delete_post, verify_post_password, BRANDS, CATEGORIES

st.set_page_config(page_title="게시글 수정", page_icon="🛠️", layout="wide")

if st.button("← 목록으로 가기"):
    st.switch_page("pages/community.py")

st.title("🛠️ 게시글 수정")

post_id = st.session_state.get("edit_post_id")

if not post_id:
    st.warning("수정할 게시글이 선택되지 않았습니다. 목록 페이지에서 '수정' 버튼을 눌러 접근해 주세요.")
    st.stop()

post = get_post(post_id)

if post is None:
    st.warning("존재하지 않는 게시글입니다.")
    st.stop()

with st.form("edit_form"):
    title = st.text_input("제목 *", value=post["title"])
    col1, col2, col3 = st.columns(3)
    with col1:
        brand = st.selectbox("브랜드", BRANDS, index=BRANDS.index(post["brand"]) if post["brand"] in BRANDS else 0)
    with col2:
        model = st.text_input("모델명", value=post["model"] or "")
    with col3:
        category = st.selectbox(
            "카테고리", CATEGORIES,
            index=CATEGORIES.index(post["category"]) if post["category"] in CATEGORIES else 0,
        )
    content = st.text_area("내용 *", value=post["content"], height=220)
    password_input = st.text_input("비밀번호 확인 *", type="password", placeholder="게시글 작성 시 등록한 비밀번호를 입력하세요.")

    submitted = st.form_submit_button("수정 완료", type="primary", use_container_width=True)

    if submitted:
        if not title.strip() or not content.strip():
            st.error("제목과 내용은 필수 입력 항목입니다.")
        elif not password_input.strip():
            st.error("수정하려면 작성 시 입력한 비밀번호를 입력해야 합니다.")
        elif not verify_post_password(post_id, password_input.strip()):
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            update_post(post_id, title.strip(), content.strip(), brand, model.strip(), category)
            st.success("게시글이 수정되었습니다!")
            del st.session_state["edit_post_id"]
            st.switch_page("pages/community.py")