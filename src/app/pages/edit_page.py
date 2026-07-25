import streamlit as st
from db_utils import get_post, update_post, delete_post, BRANDS, CATEGORIES

st.set_page_config(page_title="글 수정", page_icon="🛠️", layout="wide")

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

    save_col, delete_col = st.columns([3, 1])
    with save_col:
        submitted = st.form_submit_button("수정 완료", type="primary", use_container_width=True)
    with delete_col:
        deleted = st.form_submit_button("삭제", use_container_width=True)

    if submitted:
        if not title.strip() or not content.strip():
            st.error("제목과 내용은 필수 입력 항목입니다.")
        else:
            update_post(post_id, title.strip(), content.strip(), brand, model.strip(), category)
            st.success("게시글이 수정되었습니다!")
            del st.session_state["edit_post_id"]
            st.switch_page("pages/community.py")

    if deleted:
        delete_post(post_id)
        st.success("게시글이 삭제되었습니다.")
        del st.session_state["edit_post_id"]
        st.switch_page("pages/community.py")