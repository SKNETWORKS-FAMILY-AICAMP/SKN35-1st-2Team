import os
import sys
import math
import re
import streamlit as st

# 1. 모듈 경로 설정: src 및 프로젝트 루트 디렉터리를 sys.path 최상단에 추가하여 DB 유틸리티 등 모듈 접근 가능
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. 모듈 핫 리로드 설정 (개발 중 db_utils 수정 사항 즉시 반영)
import importlib
import db.db_utils
importlib.reload(db.db_utils)

from db.db_utils import (
    get_posts, count_comments,
    BRANDS, CATEGORIES,
)

# 페이징 설정: 페이지당 게시글 10개, 하단 번호 버튼 5개씩 노출
POSTS_PER_PAGE = 10
PAGE_BLOCK_SIZE = 5


def highlight_text(text: str, keyword: str) -> str:
    """텍스트 내 검색어를 대소문자 구분 없이 노란색 형광펜 하이라이트 HTML 태그로 반환하는 유틸리티 함수"""
    if not text or not keyword or not keyword.strip():
        return text
    kw = re.escape(keyword.strip())
    pattern = re.compile(f"({kw})", re.IGNORECASE)
    return pattern.sub(
        r'<mark style="background-color: #ffe066; color: #111; padding: 2px 5px; border-radius: 4px; font-weight: bold;">\1</mark>',
        text,
    )


# 3. Streamlit 페이지 기본 레이아웃 설정
st.set_page_config(page_title="소통공간", page_icon="💬", layout="wide")


# 상단 타이틀 및 가이드 텍스트
st.title("💬 소통공간")
st.write("차량 리콜 경험, 정보, 대응 방법 등을 자유롭게 공유해 주세요.")

# 4. 검색 필터 유지용 세션 상태(st.session_state) 초기화 (다른 페이지 방문 후 복귀 시 검색 조건 보존)
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
    """사용자가 위젯 필터를 변경할 때마다 저장용 세션 상태와 동기화하고 페이지 번호를 1페이지로 리셋"""
    st.session_state["saved_brand"] = st.session_state.get("list_brand", "전체")
    st.session_state["saved_category"] = st.session_state.get("list_category", "전체")
    st.session_state["saved_target"] = st.session_state.get("list_target", "전체")
    st.session_state["saved_keyword"] = st.session_state.get("list_keyword", "")
    st.session_state["saved_sort"] = st.session_state.get("list_sort", "최신순")
    st.session_state["community_page"] = 1


def reset_filters():
    """검색 조건 초기화 버튼 클릭 시 모든 필터 및 위젯 세션을 기본값으로 리셋"""
    for k, v in SEARCH_DEFAULTS.items():
        st.session_state[k] = v
    # UI 위젯 키 세션 값도 기본값으로 동기화
    st.session_state["list_brand"] = "전체"
    st.session_state["list_category"] = "전체"
    st.session_state["list_target"] = "전체"
    st.session_state["list_keyword"] = ""
    st.session_state["list_sort"] = "최신순"


# 5. 검색 필터 UI 영역 구성 (보존된 세션 값 기반 선택 인덱스 바인딩)
brand_options = ["전체"] + BRANDS
brand_idx = brand_options.index(st.session_state["saved_brand"]) if st.session_state["saved_brand"] in brand_options else 0

cat_options = ["전체"] + CATEGORIES
cat_idx = cat_options.index(st.session_state["saved_category"]) if st.session_state["saved_category"] in cat_options else 0

target_options = ["전체", "제목만", "내용만", "제목+내용"]
target_idx = target_options.index(st.session_state["saved_target"]) if st.session_state["saved_target"] in target_options else 0

sort_options = ["최신순", "조회순", "공감순"]
sort_idx = sort_options.index(st.session_state["saved_sort"]) if st.session_state["saved_sort"] in sort_options else 0

# 필터 5개 컬럼 레이아웃 생성
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

# 초기화 및 검색 실행 버튼
_, btn_col1, btn_col2 = st.columns([4, 1, 1])
with btn_col1:
    st.button("초기화", use_container_width=True, on_click=reset_filters)
with btn_col2:
    if st.button("🔍 검색", type="primary", use_container_width=True):
        sync_search_filters()
        st.rerun()


# 6. 현재 검색 필터 값을 변수에 할당
brand_filter = st.session_state["saved_brand"]
category_filter = st.session_state["saved_category"]
search_target = st.session_state["saved_target"]
keyword = st.session_state["saved_keyword"]
sort_by = st.session_state["saved_sort"]

st.divider()


# 7. DB에서 필터 및 정렬 조건에 맞는 게시글 목록 조회
posts = get_posts(brand_filter, category_filter, keyword, sort_by, search_target)
total_posts_count = len(posts)

# 8. 페이지네이션 범위 계산 (현재 페이지 유효 범위 계산 및 10개 슬라이싱)
total_pages = max(1, math.ceil(total_posts_count / POSTS_PER_PAGE))
current_page = min(max(1, st.session_state["community_page"]), total_pages)
st.session_state["community_page"] = current_page

start_idx = (current_page - 1) * POSTS_PER_PAGE
end_idx = start_idx + POSTS_PER_PAGE
page_posts = posts[start_idx:end_idx]

# 9. 상단 서브 헤더 (검색 결과 건수 및 글쓰기 버튼)
active_filters = brand_filter != "전체" or category_filter != "전체" or bool(keyword.strip())
count_txt = f"🔎 검색 결과: **{total_posts_count}건**" if active_filters else f"전체 게시글: **{total_posts_count}건**"

info_col, write_col = st.columns([5, 1])
with info_col:
    st.caption(f"{count_txt} (페이지 {current_page} / {total_pages})")
with write_col:
    if st.button("✏️ 글쓰기", type="primary", use_container_width=True):
        st.switch_page("pages/create_page.py")


# 10. 커스텀 CSS 스타일링: 제목 버튼을 일반 텍스트 링크처럼 보이도록 기본 버튼 스타일 오버라이딩
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


# 11. 게시글 카드 목록 렌더링 루프
if not page_posts:
    st.info("검색 결과가 없습니다. 검색어나 필터를 변경해 보세요." if active_filters
             else "아직 등록된 게시글이 없습니다. 위의 '글쓰기' 버튼으로 첫 게시글을 작성해 보세요!")
else:
    for post in page_posts:
        with st.container(border=True):
            top_l, top_r = st.columns([4, 1.8])
            with top_l:
                # 11-1. 브랜드 및 카테고리 HTML 태그 뱃지 표시
                brand_badge = f'<span style="background-color: #e7f5ff; color: #1c7ed6; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-right: 6px;">{post["brand"] or "기타"}</span>'
                cat_badge = f'<span style="background-color: #f1f3f5; color: #495057; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600;">{post["category"] or "기타"}</span>'
                st.markdown(f"{brand_badge}{cat_badge}", unsafe_allow_html=True)
            with top_r:
                # 11-2. 우측 상단 메타 통계 정보 (조회수, 좋아요/공감수, 댓글수)
                views_count = post.get("views") or 0
                st.markdown(
                    f'<div style="font-size: 18px; font-weight: 700; text-align: right; color: #333; line-height: 1;">'
                    f'👁️ {views_count} &nbsp;&nbsp; 👍 {post["likes"]} &nbsp;&nbsp; 💬 {count_comments(post["id"])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # 11-3. 게시글 제목 버튼 클릭 시 상세 페이지(detail_page.py)로 이동하며 세션에 post_id 등록
            if st.button(post['title'], key=f"title_{post['id']}", help="클릭하여 게시글 상세 읽기"):
                st.session_state["detail_post_id"] = post["id"]
                st.switch_page("pages/detail_page.py")

            # 11-4. 하단 부가 작성 정보 (모델명, 작성자 닉네임, 작성일시)
            model_txt = f"모델: {post['model']}  |  " if post["model"] else ""
            st.caption(f"{model_txt}작성자: {post['author'] or '익명'}  |  {post['created_at']}")


# 12. 하단 5-Block 네비게이션 페이징 바 컨트롤러
st.divider()

# 5개 단위 고정 블록 페이지 번호 범위 계산 (1~5, 6~10 등)
block_start = ((current_page - 1) // PAGE_BLOCK_SIZE) * PAGE_BLOCK_SIZE + 1
block_end = block_start + PAGE_BLOCK_SIZE - 1

# 중앙 영역 5개 네비게이션 버튼 배치 (처음, 이전, 1~5 숫자 번호, 다음, 마지막)
_, center_box, _ = st.columns([0.8, 2.8, 0.8])
with center_box:
    c_first, c_prev, c_nums, c_next, c_last = st.columns([1, 1, 3.2, 1, 1])
    
    # 12-1. 첫 페이지 이동 버튼
    with c_first:
        if st.button("« 처음", disabled=(current_page <= 1), use_container_width=True, help="첫 페이지로 이동"):
            st.session_state["community_page"] = 1
            st.rerun()

    # 12-2. 이전 페이지 이동 버튼
    with c_prev:
        if st.button("◀ 이전", disabled=(current_page <= 1), use_container_width=True, help="이전 페이지로 이동"):
            st.session_state["community_page"] = current_page - 1
            st.rerun()

    # 12-3. 5개 고정 번호 버튼 생성
    with c_nums:
        block_pages = list(range(block_start, block_end + 1))
        page_cols = st.columns(5)
        for idx, p_num in enumerate(block_pages):
            with page_cols[idx]:
                p_type = "primary" if p_num == current_page else "secondary"
                is_disabled = (p_num > total_pages)  # 전체 페이지 수 초과 시 비활성화
                if st.button(str(p_num), key=f"page_num_{p_num}", type=p_type, disabled=is_disabled, use_container_width=True):
                    st.session_state["community_page"] = p_num
                    st.rerun()

    # 12-4. 다음 페이지 이동 버튼
    with c_next:
        if st.button("다음 ▶", disabled=(current_page >= total_pages), use_container_width=True, help="다음 페이지로 이동"):
            st.session_state["community_page"] = current_page + 1
            st.rerun()

    # 12-5. 마지막 페이지 이동 버튼
    with c_last:
        if st.button("마지막 »", disabled=(current_page >= total_pages), use_container_width=True, help="마지막 페이지로 이동"):
            st.session_state["community_page"] = total_pages
            st.rerun()

