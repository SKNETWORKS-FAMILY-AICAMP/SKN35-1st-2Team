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
import src.db.news.db_utils
importlib.reload(src.db.news.db_utils)

from src.db.news.db_utils import (
    get_posts, count_comments,
    BRANDS, CATEGORIES,
)

# 페이징 설정: 페이지당 게시글 10개, 하단 번호 버튼 5개씩 노출
POSTS_PER_PAGE = 10
PAGE_BLOCK_SIZE = 5

# 브랜드 컬러 시스템 (service_center.py와 동일)
BRAND_COLORS = {
    "현대": {"main": "#00AAD2", "dark": "#00728C"},
    "기아": {"main": "#BB162B", "dark": "#8C0F20"},
    "벤츠": {"main": "#1A1A1A", "dark": "#000000"},
    "BMW": {"main": "#0066B1", "dark": "#003D6B"},
    "폭스바겐": {"main": "#001E50", "dark": "#000E28"},
}
DEFAULT_BRAND_COLOR = {"main": "#1c7ed6", "dark": "#1864ab"}

# 이 페이지의 공통 액센트 (특정 게시글 브랜드와 무관한 UI 요소용)
DEFAULT_ACCENT = {"main": "#2563EB", "dark": "#1D4ED8"}
ACCENT = DEFAULT_ACCENT["main"]
ACCENT_DARK = DEFAULT_ACCENT["dark"]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


ACCENT_SOFT = hex_to_rgba(ACCENT, 0.08)
ACCENT_SOFT_STRONG = hex_to_rgba(ACCENT, 0.16)


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
st.set_page_config(page_title="Community", layout="wide")

# ==========================
# Custom CSS (service_center.py와 동일한 디자인 토큰)
# ==========================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        --accent: {ACCENT};
        --accent-dark: {ACCENT_DARK};
        --accent-soft: {ACCENT_SOFT};
        --accent-soft-strong: {ACCENT_SOFT_STRONG};
        --ink: #0F172A;
        --ink-soft: #64748B;
        --line: #E7EAF0;
        --surface: #FFFFFF;
        --canvas: #F6F8FB;
    }}

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--canvas);
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1360px;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] input {{
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        box-shadow: none !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:hover {{
        border-color: var(--accent) !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: var(--ink) !important;
        fill: var(--ink) !important;
    }}
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p {{
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        line-height: 1.15rem !important;
        letter-spacing: 0.01em;
        color: var(--ink-soft) !important;
        text-transform: uppercase;
    }}

    /* ---------- 헤더 ---------- */
    .main-header {{
        margin-bottom: 1.2rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--line);
    }}
    .main-header .eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 0.55rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .main-header .eyebrow::before {{
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 0 4px var(--accent-soft);
    }}
    .main-header h1 {{
        font-family: 'Manrope', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 800 !important;
        color: var(--ink) !important;
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.03em;
    }}
    .main-header p {{
        color: var(--ink-soft) !important;
        font-size: 0.94rem;
        margin: 0;
    }}

    /* ---------- 필터 패널 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    /* ---------- 버튼 ---------- */
    div.stButton > button {{
        width: 100% !important;
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border-radius: 9px;
        height: 2.7rem;
        font-weight: 700;
        font-size: 0.95rem;
        border: none !important;
        transition: all 0.15s ease-in-out;
        box-shadow: 0 4px 12px var(--accent-soft-strong);
        letter-spacing: -0.01em;
    }}
    div.stButton > button:hover {{
        background: var(--accent-dark) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px var(--accent-soft-strong);
    }}
    /* '초기화' 버튼은 보조 톤으로 구분 */
    div[class*="st-key-reset_btn"] div.stButton > button {{
        background: var(--surface) !important;
        color: var(--ink-soft) !important;
        border: 1px solid var(--line) !important;
        box-shadow: none !important;
    }}
    div[class*="st-key-reset_btn"] div.stButton > button:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: none;
    }}

    /* ---------- 결과 요약 바 ---------- */
    .result-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 10px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.1rem;
        font-size: 0.92rem;
        color: var(--ink) !important;
    }}
    .result-bar .result-count {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--accent);
    }}

    /* ---------- 게시글 제목 버튼 (배경 없는 링크 스타일 유지) ---------- */
    div[class*="st-key-title_"] button,
    div[class*="st-key-title_"] button *,
    div[class*="st-key-title_"] button p,
    div[class*="st-key-title_"] button span {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 4px 0 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        text-align: left !important;
        box-shadow: none !important;
        outline: none !important;
        line-height: 1.4 !important;
        cursor: pointer !important;
        width: auto !important;
        height: auto !important;
    }}
    div[class*="st-key-title_"] button:hover,
    div[class*="st-key-title_"] button:hover *,
    div[class*="st-key-title_"] button:active,
    div[class*="st-key-title_"] button:focus {{
        color: var(--accent) !important;
        text-decoration: underline !important;
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        transform: none !important;
    }}

    /* 페이징 버튼 줄바꿈 방지 */
    div[data-testid="stHorizontalBlock"] button {{
        white-space: nowrap !important;
        word-break: keep-all !important;
    }}
    div[class*="st-key-cpage_"] button,
    div[class*="st-key-cpage_"] button *,
    div[class*="st-key-cpage_"] button p {{
        font-size: 13px !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow: visible !important;
    }}
    div[class*="st-key-cpage_first"] button,
    div[class*="st-key-cpage_prev"] button,
    div[class*="st-key-cpage_next"] button,
    div[class*="st-key-cpage_last"] button,
    div[class*="st-key-cpage_first"] button *,
    div[class*="st-key-cpage_prev"] button *,
    div[class*="st-key-cpage_next"] button *,
    div[class*="st-key-cpage_last"] button * {{
        font-size: 11.5px !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 상단 타이틀 및 가이드 텍스트
st.markdown(
    """
    <div class="main-header">
        <div class="eyebrow">Owner Community</div>
        <h1>Community</h1>
        <p>차량 리콜 경험, 정보, 대응 방법 등을 자유롭게 공유해 주세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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

# 필터 및 검색/초기화 버튼 통합 7컬럼 레이아웃 생성
with st.container(border=True):
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1.0, 1.1, 1.0, 2.0, 0.9, 0.75, 0.75])
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
    with col6:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 검색", type="primary", use_container_width=True):
            sync_search_filters()
            st.rerun()
    with col7:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        with st.container(key="reset_btn"):
            st.button("초기화", use_container_width=True, on_click=reset_filters)


# 6. 현재 검색 필터 값을 변수에 할당
brand_filter = st.session_state["saved_brand"]
category_filter = st.session_state["saved_category"]
search_target = st.session_state["saved_target"]
keyword = st.session_state["saved_keyword"]
sort_by = st.session_state["saved_sort"]


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
count_txt = f"🔎 검색 결과" if active_filters else "전체 게시글"

info_col, write_col = st.columns([5, 1])
with info_col:
    st.markdown(
        f"""
        <div class="result-bar">
            <span class="result-location">{count_txt} · <b>{current_page}</b> / <b>{total_pages}</b> 페이지</span>
            <span class="result-count">{total_posts_count}<span style="font-size:0.8rem;font-weight:500;color:var(--ink-soft);margin-left:0.15rem;">건</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with write_col:
    if st.button("✏️ 글쓰기", type="primary", use_container_width=True):
        st.switch_page("pages/create_page.py")


# 10. 게시글 카드 목록 렌더링 루프
if not page_posts:
    st.info("검색 결과가 없습니다. 검색어나 필터를 변경해 보세요." if active_filters
             else "아직 등록된 게시글이 없습니다. 위의 '글쓰기' 버튼으로 첫 게시글을 작성해 보세요!")
else:
    for post in page_posts:
        with st.container(border=True):
            top_l, top_r = st.columns([4, 1.8])
            with top_l:
                # 10-1. 브랜드 및 카테고리 HTML 태그 뱃지 표시 (브랜드 고유 컬러 시스템 및 좌측 border-left 액센트 적용)
                b_info = BRAND_COLORS.get(post["brand"], DEFAULT_BRAND_COLOR)
                b_main = b_info["main"]
                b_bg = hex_to_rgba(b_main, 0.12)
                b_border = hex_to_rgba(b_main, 0.25)
                accent_bar = f'<div style="border-left: 4px solid {b_main}; padding-left: 10px; margin-bottom: 4px;">'
                brand_badge = f'<span style="background-color: {b_bg}; color: {b_main}; border: 1px solid {b_border}; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 700; margin-right: 6px;">{post["brand"] or "기타"}</span>'
                cat_badge = f'<span style="background-color: #f1f3f5; color: #495057; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: 600;">{post["category"] or "기타"}</span>'
                st.markdown(f"{accent_bar}{brand_badge}{cat_badge}</div>", unsafe_allow_html=True)
            with top_r:
                # 10-2. 우측 상단 메타 통계 정보 (조회수, 좋아요/공감수, 댓글수)
                views_count = post.get("views") or 0
                st.markdown(
                    f'<div style="font-size: 18px; font-weight: 700; text-align: right; color: var(--ink); line-height: 1;">'
                    f'👁️ {views_count} &nbsp;&nbsp; 👍 {post["likes"]} &nbsp;&nbsp; 💬 {count_comments(post["id"])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # 10-3. 게시글 제목 버튼 클릭 시 상세 페이지(detail_page.py)로 이동하며 세션에 post_id 등록
            if st.button(post['title'], key=f"title_{post['id']}", help="클릭하여 게시글 상세 읽기"):
                st.session_state["detail_post_id"] = post["id"]
                st.switch_page("pages/detail_page.py")

            # 10-4. 하단 부가 작성 정보 (모델명, 작성자 닉네임, 작성일시)
            model_txt = f"모델: {post['model']}  |  " if post["model"] else ""
            st.caption(f"{model_txt}작성자: {post['author'] or '익명'}  |  {post['created_at']}")


st.divider()

# 11. 하단 동적 페이징 인디케이터 (버튼 텍스트 잘림 방지 및 비례 컬럼 가로배치)
block_start = ((current_page - 1) // PAGE_BLOCK_SIZE) * PAGE_BLOCK_SIZE + 1
block_end = block_start + PAGE_BLOCK_SIZE - 1
valid_pages = list(range(block_start, min(block_end, total_pages) + 1))

def go_community_page(p):
    st.session_state["community_page"] = p

_, center_box, _ = st.columns([0.6, 2.8, 0.6])
with center_box:
    # 축소된 네비게이션 버튼 0.95 비율, 숫자 버튼 0.8 비율
    col_weights = [0.95, 0.95] + [0.8] * len(valid_pages) + [0.95, 0.95]
    p_cols = st.columns(col_weights)

    # 11-1. 첫 페이지 이동 버튼
    with p_cols[0]:
        if st.button("« 처음", key="cpage_first", disabled=(current_page <= 1), use_container_width=True, help="첫 페이지로 이동"):
            go_community_page(1)
            st.rerun()

    # 11-2. 이전 페이지 이동 버튼
    with p_cols[1]:
        if st.button("◀ 이전", key="cpage_prev", disabled=(current_page <= 1), use_container_width=True, help="이전 페이지로 이동"):
            go_community_page(max(1, current_page - 1))
            st.rerun()

    # 11-3. 데이터가 존재하는 유효한 페이지 번호 버튼만 표시
    for idx, p_num in enumerate(valid_pages):
        with p_cols[2 + idx]:
            p_type = "primary" if p_num == current_page else "secondary"
            if st.button(str(p_num), key=f"cpage_btn_{p_num}", type=p_type, use_container_width=True):
                go_community_page(p_num)
                st.rerun()

    # 11-4. 다음 페이지 이동 버튼
    with p_cols[2 + len(valid_pages)]:
        if st.button("다음 ▶", key="cpage_next", disabled=(current_page >= total_pages), use_container_width=True, help="다음 페이지로 이동"):
            go_community_page(min(total_pages, current_page + 1))
            st.rerun()

    # 11-5. 마지막 페이지 이동 버튼
    with p_cols[3 + len(valid_pages)]:
        if st.button("마지막 »", key="cpage_last", disabled=(current_page >= total_pages), use_container_width=True, help="마지막 페이지로 이동"):
            go_community_page(total_pages)
            st.rerun()