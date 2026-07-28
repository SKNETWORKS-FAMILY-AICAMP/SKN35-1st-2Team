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
import src.db.news.db_utils
importlib.reload(src.db.news.db_utils)

from src.db.news.db_utils import get_news, count_news, get_news_sources

NEWS_PER_PAGE = 8
PAGE_BLOCK_SIZE = 5

# ==========================
# 디자인 토큰 (service_center.py와 동일한 기본 액센트)
# ==========================
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
    """텍스트 내 검색어를 대소문자 구분 없이 노란색 형광펜 하이라이트로 반환"""
    if not text or not keyword or not keyword.strip():
        return text
    kw = re.escape(keyword.strip())
    pattern = re.compile(f"({kw})", re.IGNORECASE)
    return pattern.sub(
        r'<mark style="background-color: #ffe066; color: #111; padding: 2px 5px; border-radius: 4px; font-weight: bold;">\1</mark>',
        text,
    )


# 1. 페이지 기본 설정 및 커스텀 CSS (service_center.py와 동일한 디자인 토큰)
st.set_page_config(page_title="News", layout="wide")

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
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.6rem;
        padding-bottom: 1.4rem;
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

    /* 상단 '뉴스 상세 확인하기' 링크 버튼 → 브랜드 칩 스타일 */
    a.news-link-btn {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        color: #FFFFFF !important;
        background: var(--accent) !important;
        padding: 0.55rem 1.05rem !important;
        border-radius: 999px !important;
        white-space: nowrap !important;
        box-shadow: 0 6px 16px var(--accent-soft-strong) !important;
        text-decoration: none !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}
    a.news-link-btn:hover {{
        background: var(--accent-dark) !important;
        color: #FFFFFF !important;
        text-decoration: none !important;
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
        padding: 0.85rem 1.2rem;
        margin-top: 1.0rem;
        margin-bottom: 1.1rem;
        font-size: 0.92rem;
        color: var(--ink) !important;
    }}
    .result-bar .result-count {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--accent);
    }}

    /* ---------- 뉴스 카드 ---------- */
    .news-title {{
        font-family: 'Manrope', sans-serif;
        font-size: 22px;
        font-weight: 800;
        line-height: 1.4;
        color: var(--ink) !important;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }}
    .news-summary-box {{
        background: var(--canvas) !important;
        border: 1px solid var(--line) !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
    }}
    .news-summary-text {{
        font-size: 14.5px !important;
        line-height: 1.4em !important;
        max-height: 2.8em !important;
        color: var(--ink) !important;
        margin: 0 !important;
        padding: 0 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        word-break: break-all !important;
    }}
    .news-summary-text mark {{
        color: #111111 !important;
    }}

    /* 하단 페이징 버튼 */
    div[class*="st-key-p_"] button,
    div[class*="st-key-p_"] button *,
    div[class*="st-key-p_"] button p {{
        font-size: 13px !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow: visible !important;
    }}
    div[class*="st-key-p_first"] button,
    div[class*="st-key-p_prev"] button,
    div[class*="st-key-p_next"] button,
    div[class*="st-key-p_last"] button,
    div[class*="st-key-p_first"] button *,
    div[class*="st-key-p_prev"] button *,
    div[class*="st-key-p_next"] button *,
    div[class*="st-key-p_last"] button * {{
        font-size: 11.5px !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# 2. 상단 헤더 및 뉴스 상세 이동 버튼 (우측 정렬)
st.markdown(
    """
    <div class="main-header">
        <div>
            <div class="eyebrow">Recall News Feed</div>
            <h1>News</h1>
            <p>자동차 리콜·결함 관련 최신 뉴스를 한눈에 확인해 보세요.</p>
        </div>
        <a href="https://www.car.go.kr/sd/newsDta/list.do" target="_blank" rel="noopener noreferrer" class="news-link-btn">
           📰 뉴스 상세 확인하기
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3. 검색 필터 세션 상태 초기화 (페이지 이동 후 복귀 시 100% 필터 유지)
NEWS_SEARCH_DEFAULTS = {
    "saved_news_source": "전체",
    "saved_news_keyword": "",
    "saved_news_sort": "최신순",
    "news_page": 1,
}
for k, v in NEWS_SEARCH_DEFAULTS.items():
    st.session_state.setdefault(k, v)


def sync_news_filters():
    st.session_state["saved_news_source"] = st.session_state.get("news_source", "전체")
    st.session_state["saved_news_keyword"] = st.session_state.get("news_keyword", "")
    st.session_state["saved_news_sort"] = st.session_state.get("news_sort", "최신순")
    st.session_state["news_page"] = 1


def reset_news_filters():
    for k, v in NEWS_SEARCH_DEFAULTS.items():
        st.session_state[k] = v
    st.session_state["news_source"] = "전체"
    st.session_state["news_keyword"] = ""
    st.session_state["news_sort"] = "최신순"


# 4. 검색 필터 및 입력 영역 (언론사/출처 필터 추가 & 오래된순 정렬)
available_sources = ["전체"] + get_news_sources()
source_idx = available_sources.index(st.session_state["saved_news_source"]) if st.session_state["saved_news_source"] in available_sources else 0

sort_options = ["최신순", "오래된순"]
sort_idx = sort_options.index(st.session_state["saved_news_sort"]) if st.session_state["saved_news_sort"] in sort_options else 0

with st.container(border=True):
    col1, col2, col3, col4, col5 = st.columns([1.1, 2.5, 0.9, 0.75, 0.75])
    with col1:
        st.selectbox(
            "출처",
            available_sources,
            index=source_idx,
            key="news_source",
            on_change=sync_news_filters,
        )
    with col2:
        st.text_input(
            "검색어",
            value=st.session_state["saved_news_keyword"],
            placeholder="뉴스 제목으로 검색",
            key="news_keyword",
            on_change=sync_news_filters,
        )
    with col3:
        st.selectbox(
            "정렬",
            sort_options,
            index=sort_idx,
            key="news_sort",
            on_change=sync_news_filters,
        )
    with col4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 검색", type="primary", use_container_width=True):
            sync_news_filters()
            st.rerun()
    with col5:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        with st.container(key="reset_btn"):
            st.button("초기화", use_container_width=True, on_click=reset_news_filters)


# 5. 현재 검색 조건 변수 할당
source_filter = st.session_state["saved_news_source"]
keyword = st.session_state["saved_news_keyword"]
sort_by = st.session_state["saved_news_sort"]


# 6. MySQL 데이터베이스에서 리콜 뉴스 조회
all_news = get_news(keyword, source_filter, sort_by)
total_count = len(all_news)

# 페이지네이션 계산
total_pages = max(1, math.ceil(total_count / NEWS_PER_PAGE))
current_page = min(max(1, st.session_state["news_page"]), total_pages)
st.session_state["news_page"] = current_page

start_idx = (current_page - 1) * NEWS_PER_PAGE
end_idx = start_idx + NEWS_PER_PAGE
page_news = all_news[start_idx:end_idx]


# 7. 검색 결과 건수 표시
active_filters = bool(keyword.strip())
result_label = "🔎 검색 결과" if active_filters else "전체 리콜 뉴스"
st.markdown(
    f"""
    <div class="result-bar">
        <span class="result-location">{result_label} · <b>{current_page}</b> / <b>{total_pages}</b> 페이지</span>
        <span class="result-count">{total_count}<span style="font-size:0.85rem;font-weight:500;color:var(--ink-soft);margin-left:0.15rem;">건</span></span>
    </div>
    """,
    unsafe_allow_html=True,
)


# 8. 뉴스 렌더링 영역
if not page_news:
    st.info(
        "검색 결과가 없습니다. 검색어를 변경해 보세요."
        if active_filters
        else "아직 등록된 리콜 뉴스가 없습니다."
    )
else:
    for news in page_news:
        with st.container(border=True):
            top_c1, top_c2 = st.columns([4, 1.2])
            with top_c1:
                highlighted_title = highlight_text(news['title'], keyword)
                st.markdown(f'<div class="news-title">{highlighted_title}</div>', unsafe_allow_html=True)
            with top_c2:
                st.markdown(
                    f'<div style="text-align: right; color: var(--accent); font-size: 14px; font-weight: 600;">'
                    f'📰 {news["source"] or "국토교통부"}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.caption(f"📅 보도일자: **{news['published_at']}**")

            summary_txt = news["summary"] or "요약 정보가 없습니다."
            highlighted_summary = highlight_text(summary_txt, keyword)
            st.markdown(
                f'<div class="news-summary-box">'
                f'<p class="news-summary-text">{highlighted_summary}</p>'
                f'</div>',
                unsafe_allow_html=True
            )


st.divider()

# 9. 페이지 인디케이터
block_index = (current_page - 1) // PAGE_BLOCK_SIZE
block_start_page = block_index * PAGE_BLOCK_SIZE + 1
block_end_page = block_start_page + PAGE_BLOCK_SIZE - 1
valid_pages = list(range(block_start_page, min(block_end_page, total_pages) + 1))

def go_page(p):
    st.session_state["news_page"] = p

_, center_page_col, _ = st.columns([0.6, 2.8, 0.6])
with center_page_col:
    # 축소된 네비게이션 버튼 0.95 비율, 숫자 버튼 0.8 비율
    col_weights = [0.95, 0.95] + [0.8] * len(valid_pages) + [0.95, 0.95]
    p_cols = st.columns(col_weights)

    # 1. 맨 첫 페이지 이동 버튼
    with p_cols[0]:
        if st.button("« 처음", key="p_first", use_container_width=True, disabled=(current_page == 1)):
            go_page(1)
            st.rerun()

    # 2. 이전 페이지 이동 버튼
    with p_cols[1]:
        prev_target = max(1, current_page - 1)
        if st.button("◀ 이전", key="p_prev", use_container_width=True, disabled=(current_page == 1)):
            go_page(prev_target)
            st.rerun()

    # 3. 데이터가 존재하는 유효한 페이지 번호 버튼만 표시
    for idx, p_num in enumerate(valid_pages):
        with p_cols[2 + idx]:
            btn_type = "primary" if p_num == current_page else "secondary"
            if st.button(str(p_num), key=f"p_btn_{p_num}", type=btn_type, use_container_width=True):
                go_page(p_num)
                st.rerun()

    # 4. 다음 페이지 이동 버튼
    with p_cols[2 + len(valid_pages)]:
        next_target = min(total_pages, current_page + 1)
        if st.button("다음 ▶", key="p_next", use_container_width=True, disabled=(current_page == total_pages)):
            go_page(next_target)
            st.rerun()

    # 5. 맨 마지막 페이지 이동 버튼
    with p_cols[3 + len(valid_pages)]:
        if st.button("마지막 »", key="p_last", use_container_width=True, disabled=(current_page == total_pages)):
            go_page(total_pages)
            st.rerun()