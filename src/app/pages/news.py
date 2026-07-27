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

from db.db_utils import get_news, count_news, get_news_sources

NEWS_PER_PAGE = 8
PAGE_BLOCK_SIZE = 5


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


# 1. 페이지 기본 설정 및 다크모드 대응 커스텀 CSS
st.set_page_config(page_title="News", layout="wide")

st.markdown(
    """
    <style>
    /* 상단 '뉴스 상세 확인하기' 링크 버튼 (Streamlit 기본 마크다운 <a> 스타일 완전 오버라이드) */
    a.news-link-btn,
    div[data-testid="stMarkdownContainer"] a.news-link-btn,
    .stMarkdown a.news-link-btn,
    a.news-link-btn:hover,
    a.news-link-btn:focus,
    a.news-link-btn:active {
        text-decoration: none !important;
    }
    a.news-link-btn,
    div[data-testid="stMarkdownContainer"] a.news-link-btn,
    .stMarkdown a.news-link-btn {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        padding: 7px 16px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    a.news-link-btn:hover,
    div[data-testid="stMarkdownContainer"] a.news-link-btn:hover {
        background-color: #f8f9fa !important;
        color: #111827 !important;
        border-color: #c1c7d0 !important;
        text-decoration: none !important;
    }

    .news-title {
        font-size: 22px;
        font-weight: 700;
        line-height: 1.4;
        color: inherit !important;
        margin-bottom: 4px;
    }
    /* 뉴스 본문 카드 요약 외곽 상자 */
    .news-summary-box {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        margin: 10px 0 !important;
        overflow: hidden !important;
    }

    /* 뉴스 본문 카드 요약 2줄 제한 텍스트 (패딩 0으로 3번째 줄 유출 차단) */
    .news-summary-text {
        font-size: 14.5px !important;
        line-height: 1.4em !important;
        max-height: 2.8em !important; /* 1.4em * 2줄 = 정확히 2.8em */
        color: inherit !important;
        margin: 0 !important;
        padding: 0 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        word-break: break-all !important;
    }
    .news-summary-text mark {
        color: #111111 !important;
    }

    /* 다크모드 대응 (OS/브라우저 및 Streamlit 설정 다크 테마 지원) */
    @media (prefers-color-scheme: dark) {
        a.news-link-btn,
        div[data-testid="stMarkdownContainer"] a.news-link-btn,
        .stMarkdown a.news-link-btn {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            box-shadow: none !important;
        }
        a.news-link-btn:hover,
        div[data-testid="stMarkdownContainer"] a.news-link-btn:hover {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            text-decoration: none !important;
        }
        .news-summary-box {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }
        .news-summary-text {
            color: #ffffff !important;
        }
        .news-title {
            color: #e2e8f0 !important;
        }
        div[data-testid="stCaptionContainer"],
        div[data-testid="stCaptionContainer"] * {
            color: #cbd5e1 !important;
        }
    }

    [data-theme="dark"] a.news-link-btn,
    .stApp[data-theme="dark"] a.news-link-btn,
    [data-testid="stAppViewContainer"][data-theme="dark"] a.news-link-btn,
    div[data-testid="stMarkdownContainer"][data-theme="dark"] a.news-link-btn,
    .stApp.dark a.news-link-btn,
    body.dark a.news-link-btn,
    html.dark a.news-link-btn {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        box-shadow: none !important;
    }
    [data-theme="dark"] a.news-link-btn:hover,
    .stApp[data-theme="dark"] a.news-link-btn:hover,
    [data-testid="stAppViewContainer"][data-theme="dark"] a.news-link-btn:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        text-decoration: none !important;
    }

    /* 하단 페이징 버튼 */
    div[class*="st-key-p_"] button,
    div[class*="st-key-p_"] button *,
    div[class*="st-key-p_"] button p {
        font-size: 13px !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow: visible !important;
    }
    div[class*="st-key-p_first"] button,
    div[class*="st-key-p_prev"] button,
    div[class*="st-key-p_next"] button,
    div[class*="st-key-p_last"] button,
    div[class*="st-key-p_first"] button *,
    div[class*="st-key-p_prev"] button *,
    div[class*="st-key-p_next"] button *,
    div[class*="st-key-p_last"] button * {
        font-size: 11.5px !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 2. 상단 헤더 및 뉴스 상세 이동 버튼 (우측 정렬)
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 6px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 700; color: var(--text-color, inherit); white-space: nowrap; line-height: 1;">News</h1>
        <a href="https://www.car.go.kr/sd/newsDta/list.do" target="_blank" rel="noopener noreferrer" class="news-link-btn">
           뉴스 상세 확인하기 
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("자동차 리콜·결함 관련 최신 뉴스를 한눈에 확인해 보세요.")

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

col1, col2, col3, col4, col5 = st.columns([1.1, 2.5, 0.9, 0.75, 0.75])
with col1:
    st.selectbox(
        "언론사/출처",
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
    st.button("초기화", use_container_width=True, on_click=reset_news_filters)


# 5. 현재 검색 조건 변수 할당
source_filter = st.session_state["saved_news_source"]
keyword = st.session_state["saved_news_keyword"]
sort_by = st.session_state["saved_news_sort"]

st.divider()


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
if active_filters:
    st.caption(f"🔎 검색 결과: **{total_count}건** (현재 {current_page}/{total_pages} 페이지)")
else:
    st.caption(f"전체 리콜 뉴스: **{total_count}건** (현재 {current_page}/{total_pages} 페이지)")


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
                    f'<div style="text-align: right; color: #1c7ed6; font-size: 14px; font-weight: 600;">'
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