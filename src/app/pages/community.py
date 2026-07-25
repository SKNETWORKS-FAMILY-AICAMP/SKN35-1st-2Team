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

# 데이터베이스 처리를 위한 유틸리티 함수와 상수들 가져오기
from db.db_utils import (
    get_posts, like_post, get_comments, count_comments, add_comment,
    BRANDS, CATEGORIES,
)

# 1. 페이지 기본 설정
# 브라우저 탭의 제목, 아이콘을 설정하고 화면을 넓게(wide) 쓰도록 지정합니다.
st.set_page_config(page_title="소통공간", page_icon="💬", layout="wide")


# 2. 상단 헤더 및 글쓰기 버튼 영역
# 화면을 5:1 비율의 두 컬럼으로 나눕니다.

top_col1, top_col2 = st.columns([5, 1])
with top_col1:
    st.title("💬소통공간")
    st.write("차량 리콜 경험, 정보, 대응 방법 등을 자유롭게 공유해 주세요.")
with top_col2:
    st.write("") # 버튼 위치를 텍스트와 맞추기 위한 빈 여백

    # '글쓰기' 버튼 클릭 시 게시글 작성 페이지로 이동합니다. (type="primary"는 버튼을 돋보이게 함)
    if st.button("✏️ 글쓰기", type="primary", use_container_width=True):
        st.switch_page("pages/create_page.py")

# 3. 검색 필터 세션 상태(Session State) 초기화
# 페이지가 새로고침되어도 검색 조건이 유지되도록 기본값을 정의합니다.
SEARCH_DEFAULTS = {
    "list_brand": "전체",
    "list_category": "전체",
    "list_keyword": "",
    "list_sort": "최신순",
}
# session_state에 해당 키가 없으면 기본값으로 세팅합니다.
for k, v in SEARCH_DEFAULTS.items():
    st.session_state.setdefault(k, v)

# 4. 필터 초기화 콜백 함수
# 이 함수가 실행되면 세션 상태의 검색 조건들이 모두 기본값으로 리셋됩니다.
# (현재 코드에서는 아래 폼 버튼의 on_click 속성 등으로 연결해서 사용할 수 있습니다.)
def reset_filters():
    for k, v in SEARCH_DEFAULTS.items():
        st.session_state[k] = v

# 5. 검색 폼(Form) 영역
# 폼 내부의 위젯들은 값을 변경해도 바로 화면이 새로고침되지 않고, '검색' 버튼을 눌렀을 때 일괄 적용됩니다.
with st.form("search_form"):
    col1, col2, col3, col4 = st.columns([1, 1.2, 2, 0.7])
    with col1:
        st.selectbox("브랜드", ["전체"] + BRANDS, key="list_brand")
    with col2:
        st.selectbox("카테고리", ["전체"] + CATEGORIES, key="list_category")
    with col3:
        st.text_input("검색어", placeholder="제목, 내용, 모델명, 작성자로 검색", key="list_keyword")
    with col4:
        st.selectbox("정렬", ["최신순", "공감순"], key="list_sort")

    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    with btn_col1:
        st.form_submit_button("🔍 검색", type="primary", use_container_width=True)
    with btn_col2:
        reset_clicked = st.form_submit_button("초기화", use_container_width=True, on_click=reset_filters)


# 6. 현재 검색 조건 변수 할당
# 세션 상태에 저장된 현재 위젯 값들을 변수로 가져옵니다.
brand_filter = st.session_state["list_brand"]
category_filter = st.session_state["list_category"]
keyword = st.session_state["list_keyword"]
sort_by = st.session_state["list_sort"]

st.divider() # 화면에 가로 구분선 그리기


# 7. 데이터베이스에서 조건에 맞는 게시글 조회
posts = get_posts(brand_filter, category_filter, keyword, sort_by)

# 8. 검색 결과 건수 표시
# 필터가 '전체'가 아니거나 검색어가 있으면(active_filters = True) 검색 결과로 표시, 아니면 전체 글로 표시
active_filters = brand_filter != "전체" or category_filter != "전체" or bool(keyword.strip())
if active_filters:
    st.caption(f"🔎 검색 결과: **{len(posts)}건**")
else:
    st.caption(f"전체 게시글: **{len(posts)}건**")


# 9. 게시글 렌더링 영역(# 게시글이 없을 때 안내 메시지)
if not posts:
    st.info("검색 결과가 없습니다. 검색어나 필터를 변경해 보세요." if active_filters
             else "아직 등록된 게시글이 없습니다. 위의 '글쓰기' 버튼으로 첫 게시글을 작성해 보세요!")
else:
    for post in posts:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                st.markdown(f"`{post['brand'] or '기타'}`  `{post['category'] or '기타'}`")
                st.markdown(f"### {post['title']}")
            with c2:
                st.caption(f"👍 {post['likes']}  💬 {count_comments(post['id'])}")
            with c3:
                if st.button("수정", key=f"edit_{post['id']}", use_container_width=True):
                    st.session_state["edit_post_id"] = post["id"]
                    st.switch_page("pages/edit_page.py")

            model_txt = f"모델: {post['model']}  |  " if post["model"] else ""
            st.caption(f"{model_txt}작성자: {post['author'] or '익명'}  |  {post['created_at']}")

            # 10. 본문 및 댓글 토글(Expander) 영역
            # 클릭하면 아래 내용이 펼쳐집니다.
            with st.expander("내용 및 댓글 보기"):
                st.write(post["content"])

                like_col, _ = st.columns([1, 5])
                with like_col:
                    if st.button(f"👍 공감 {post['likes']}", key=f"like_{post['id']}"):
                        like_post(post["id"])
                        st.rerun()

                st.divider()
                comments = get_comments(post["id"])
                st.markdown(f"**💬 댓글 {len(comments)}개**")
                for c in comments:
                    st.markdown(f"- **{c['author'] or '익명'}** ({c['created_at']}): {c['content']}")

                # 11. 댓글 작성 폼
                # clear_on_submit=True 설정으로 폼 제출 후 입력창이 자동으로 비워집니다.
                with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                    c_author = st.text_input("닉네임", value="익명", key=f"c_author_{post['id']}")
                    c_content = st.text_area("댓글 내용", height=70, key=f"c_content_{post['id']}")
                    submitted = st.form_submit_button("댓글 등록")
                    if submitted:
                        if not c_content.strip():
                            st.error("댓글 내용을 입력해 주세요.")
                        else:
                            add_comment(post["id"], c_author.strip() or "익명", c_content.strip())
                            st.rerun()
