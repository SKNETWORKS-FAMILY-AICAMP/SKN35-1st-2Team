import os
import sys
import math
import re
import streamlit as st

# src 및 루트 디렉토리를 sys.path 최상단에 추가
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import importlib
import db.db_utils
importlib.reload(db.db_utils)

from db.db_utils import (
    get_posts, count_comments,
    BRANDS, CATEGORIES,
)

POSTS_PER_PAGE = 10
PAGE_BLOCK_SIZE = 5  # 한 번에 표시할 페이지 버튼 수 (1~5 기본 노출)


def highlight_text(text: str, keyword: str) -> str:
    """텍스트 내 검색어를 노란색 형광펜 하이라이트로 반환"""
    if not text or not keyword or not keyword.strip():
        return text
    kw = re.escape(keyword.strip())
    pattern = re.compile(f"({kw})", re.IGNORECASE)
    return pattern.sub(
        r'<mark style="background-color: #ffe066; color: #111; padding: 2px 5px; border-radius: 4px; font-weight: bold;">\1</mark>',
        text,
    )


# 1. 페이지 기본 설정
st.set_page_config(page_title="소통공간", page_icon="💬", layout="wide")


# 2. 상단 헤더 영역
st.title("💬 소통공간")
st.write("차량 리콜 경험, 정보, 대응 방법 등을 자유롭게 공유해 주세요.")

# 3. 검색 필터 보존 세션 상태 초기화 (페이지 이동 후 복귀 시 100% 필터 유지)
SEARCH_DEFAULTS = {
    "saved_brand": "전체",
    "saved_category": "전체",
    "saved_target": "전체",
    "saved_keyword": "",
    "saved_sort": "최신순",
    "community_page": 1,
}
for k, v in SEARCH_DEFAULTS.items():
    st.session_state.setdefault(k, v)


def sync_search_filters():
    st.session_state["saved_brand"] = st.session_state.get("list_brand", "전체")
    st.session_state["saved_category"] = st.session_state.get("list_category", "전체")
    st.session_state["saved_target"] = st.session_state.get("list_target", "전체")
    st.session_state["saved_keyword"] = st.session_state.get("list_keyword", "")
    st.session_state["saved_sort"] = st.session_state.get("list_sort", "최신순")
    st.session_state["community_page"] = 1


def reset_filters():
    for k, v in SEARCH_DEFAULTS.items():
        st.session_state[k] = v
    # 위젯 키 세션 동기화
    st.session_state["list_brand"] = "전체"
    st.session_state["list_category"] = "전체"
    st.session_state["list_target"] = "전체"
    st.session_state["list_keyword"] = ""
    st.session_state["list_sort"] = "최신순"


# 4. 검색 필터 및 입력 영역 (보존 세션 상태 바인딩)
brand_options = ["전체"] + BRANDS
brand_idx = brand_options.index(st.session_state["saved_brand"]) if st.session_state["saved_brand"] in brand_options else 0

cat_options = ["전체"] + CATEGORIES
cat_idx = cat_options.index(st.session_state["saved_category"]) if st.session_state["saved_category"] in cat_options else 0

target_options = ["전체", "제목만", "내용만", "제목+내용"]
target_idx = target_options.index(st.session_state["saved_target"]) if st.session_state["saved_target"] in target_options else 0

sort_options = ["최신순", "조회순", "공감순"]
sort_idx = sort_options.index(st.session_state["saved_sort"]) if st.session_state["saved_sort"] in sort_options else 0

col1, col2, col3, col4, col5 = st.columns([1, 1, 1.1, 2, 0.8])
with col1:
    st.selectbox("브랜드", brand_options, index=brand_idx, key="list_brand", on_change=sync_search_filters)
with col2:
    st.selectbox("카테고리", cat_options, index=cat_idx, key="list_category", on_change=sync_search_filters)
with col3:
    st.selectbox("검색 범위", target_options, index=target_idx, key="list_target", on_change=sync_search_filters)
with col4:
    st.text_input("검색어", value=st.session_state["saved_keyword"], placeholder="검색어를 입력하세요", key="list_keyword", on_change=sync_search_filters)
with col5:
    st.selectbox("정렬", sort_options, index=sort_idx, key="list_sort", on_change=sync_search_filters)

_, btn_col1, btn_col2 = st.columns([4, 1, 1])
with btn_col1:
    st.button("초기화", use_container_width=True, on_click=reset_filters)
with btn_col2:
    if st.button("🔍 검색", type="primary", use_container_width=True):
        sync_search_filters()
        st.rerun()


# 5. 현재 검색 조건 변수 할당
brand_filter = st.session_state["saved_brand"]
category_filter = st.session_state["saved_category"]
search_target = st.session_state["saved_target"]
keyword = st.session_state["saved_keyword"]
sort_by = st.session_state["saved_sort"]

st.divider()


# 6. 데이터베이스에서 게시글 조회
posts = get_posts(brand_filter, category_filter, keyword, sort_by, search_target)
total_posts_count = len(posts)

# 페이지네이션 계산
total_pages = max(1, math.ceil(total_posts_count / POSTS_PER_PAGE))
current_page = min(max(1, st.session_state["community_page"]), total_pages)
st.session_state["community_page"] = current_page

start_idx = (current_page - 1) * POSTS_PER_PAGE
end_idx = start_idx + POSTS_PER_PAGE
page_posts = posts[start_idx:end_idx]

# 7. 검색 결과 건수, 페이지 정보 및 글쓰기 버튼 영역
active_filters = brand_filter != "전체" or category_filter != "전체" or bool(keyword.strip())
count_txt = f"🔎 검색 결과: **{total_posts_count}건**" if active_filters else f"전체 게시글: **{total_posts_count}건**"

info_col, write_col = st.columns([5, 1])
with info_col:
    st.caption(f"{count_txt} (페이지 {current_page} / {total_pages})")
with write_col:
    if st.button("✏️ 글쓰기", type="primary", use_container_width=True):
        st.switch_page("pages/create_page.py")


# 텍스트 형태 타이틀 버튼 스타일링 (자식 <p> 태그 오버라이딩 방지 ➔ 28px 볼드체 100% 적용)
st.markdown(
    """
    <style>
    div[class*="st-key-title_"] button,
    div[class*="st-key-title_"] button *,
    div[class*="st-key-title_"] button p,
    div[class*="st-key-title_"] button span {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 4px 0 !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #111827 !important;
        text-align: left !important;
        box-shadow: none !important;
        outline: none !important;
        line-height: 1.4 !important;
        cursor: pointer !important;
    }
    div[class*="st-key-title_"] button:hover,
    div[class*="st-key-title_"] button:hover *,
    div[class*="st-key-title_"] button:active,
    div[class*="st-key-title_"] button:focus {
        color: #1c7ed6 !important;
        text-decoration: underline !important;
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 8. 게시글 목록 렌더링 영역
if not page_posts:
    st.info("검색 결과가 없습니다. 검색어나 필터를 변경해 보세요." if active_filters
             else "아직 등록된 게시글이 없습니다. 위의 '글쓰기' 버튼으로 첫 게시글을 작성해 보세요!")
else:
    for post in page_posts:
        with st.container(border=True):
            top_l, top_r = st.columns([4, 1.8])
            with top_l:
                # 포스트 태그 뱃지 UI
                brand_badge = f'<span style="background-color: #e7f5ff; color: #1c7ed6; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-right: 6px;">{post["brand"] or "기타"}</span>'
                cat_badge = f'<span style="background-color: #f1f3f5; color: #495057; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600;">{post["category"] or "기타"}</span>'
                st.markdown(f"{brand_badge}{cat_badge}", unsafe_allow_html=True)
            with top_r:
                # 카드 내 우측 상단 배치 (조회수 | 좋아요 | 댓글)
                views_count = post.get("views") or 0
                st.markdown(
                    f'<div style="font-size: 18px; font-weight: 700; text-align: right; color: #333; line-height: 1;">'
                    f'👁️ {views_count} &nbsp;&nbsp; 👍 {post["likes"]} &nbsp;&nbsp; 💬 {count_comments(post["id"])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # 가독성 높은 26px 볼드체 텍스트 제목 (클릭 시 상세 이동)
            if st.button(post['title'], key=f"title_{post['id']}", help="클릭하여 게시글 상세 읽기"):
                st.session_state["detail_post_id"] = post["id"]
                st.switch_page("pages/detail_page.py")

            model_txt = f"모델: {post['model']}  |  " if post["model"] else ""
            st.caption(f"{model_txt}작성자: {post['author'] or '익명'}  |  {post['created_at']}")


# 9. 페이지 인디케이터 (처음/마지막, 이전/다음 및 5개 고정 번호)
st.divider()

# 5개 단위 고정 블록 계산 (1~5, 6~10 ...)
block_start = ((current_page - 1) // PAGE_BLOCK_SIZE) * PAGE_BLOCK_SIZE + 1
block_end = block_start + PAGE_BLOCK_SIZE - 1

# 센터 박스에서 5단계 네비게이션 (처음, 이전, 1~5번호, 다음, 마지막)
_, center_box, _ = st.columns([0.8, 2.8, 0.8])
with center_box:
    c_first, c_prev, c_nums, c_next, c_last = st.columns([1, 1, 3.2, 1, 1])
    with c_first:
        if st.button("« 처음", disabled=(current_page <= 1), use_container_width=True, help="첫 페이지로 이동"):
            st.session_state["community_page"] = 1
            st.rerun()

    with c_prev:
        if st.button("◀ 이전", disabled=(current_page <= 1), use_container_width=True, help="이전 페이지로 이동"):
            st.session_state["community_page"] = current_page - 1
            st.rerun()

    with c_nums:
        block_pages = list(range(block_start, block_end + 1))  # 무조건 5개 번호
        page_cols = st.columns(5)
        for idx, p_num in enumerate(block_pages):
            with page_cols[idx]:
                p_type = "primary" if p_num == current_page else "secondary"
                is_disabled = (p_num > total_pages)
                if st.button(str(p_num), key=f"page_num_{p_num}", type=p_type, disabled=is_disabled, use_container_width=True):
                    st.session_state["community_page"] = p_num
                    st.rerun()

    with c_next:
        if st.button("다음 ▶", disabled=(current_page >= total_pages), use_container_width=True, help="다음 페이지로 이동"):
            st.session_state["community_page"] = current_page + 1
            st.rerun()

    with c_last:
        if st.button("마지막 »", disabled=(current_page >= total_pages), use_container_width=True, help="마지막 페이지로 이동"):
            st.session_state["community_page"] = total_pages
            st.rerun()
