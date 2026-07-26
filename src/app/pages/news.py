# 수정일자: 2026-07-26
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


# 1. 페이지 기본 설정
st.set_page_config(page_title="소식", page_icon="📰", layout="wide")


# 2. 상단 헤더
st.title("📰 소식")
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

col1, col2, col3 = st.columns([2.5, 1.2, 1])
with col1:
    st.text_input(
        "검색어",
        value=st.session_state["saved_news_keyword"],
        placeholder="뉴스 제목으로 검색",
        key="news_keyword",
        on_change=sync_news_filters,
    )
with col2:
    st.selectbox(
        "언론사/출처",
        available_sources,
        index=source_idx,
        key="news_source",
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

_, btn_col1, btn_col2 = st.columns([4, 1, 1])
with btn_col1:
    st.button("초기화", use_container_width=True, on_click=reset_news_filters)
with btn_col2:
    if st.button("🔍 검색", type="primary", use_container_width=True):
        sync_news_filters()
        st.rerun()


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
                st.markdown(f"### {highlighted_title}", unsafe_allow_html=True)
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
                f'<div style="font-size: 15px; line-height: 1.6; color: #444; background-color: #f8f9fa; padding: 12px 16px; border-radius: 6px; margin: 10px 0;">'
                f'{highlighted_summary}'
                f'</div>',
                unsafe_allow_html=True
            )

            col_link, _ = st.columns([2, 5])
            with col_link:
                st.link_button("🔗 원문 보도자료 읽기 ↗", news["url"], use_container_width=True)

st.divider()

# 9. 페이지 인디케이터 (50% 너비 구역 안 5-block 네비게이션)
block_index = (current_page - 1) // PAGE_BLOCK_SIZE
block_start_page = block_index * PAGE_BLOCK_SIZE + 1
block_end_page = block_start_page + PAGE_BLOCK_SIZE - 1

def go_page(p):
    st.session_state["news_page"] = p

_, center_page_col, _ = st.columns([1, 2, 1])
with center_page_col:
    p_cols = st.columns(PAGE_BLOCK_SIZE + 4)

    # 1. 맨 첫 페이지 이동 버튼
    with p_cols[0]:
        if st.button("« 처음", key="p_first", use_container_width=True, disabled=(current_page == 1)):
            go_page(1)
            st.rerun()

    # 2. 이전 블록 이동 버튼
    with p_cols[1]:
        prev_target = max(1, block_start_page - 1)
        if st.button("◀ 이전", key="p_prev", use_container_width=True, disabled=(block_start_page == 1)):
            go_page(prev_target)
            st.rerun()

    # 3. 5개 번호 버튼 (유효범위 지나면 disabled)
    for i in range(PAGE_BLOCK_SIZE):
        p_num = block_start_page + i
        with p_cols[2 + i]:
            btn_type = "primary" if p_num == current_page else "secondary"
            is_disabled = p_num > total_pages
            if st.button(str(p_num), key=f"p_btn_{p_num}", type=btn_type, use_container_width=True, disabled=is_disabled):
                go_page(p_num)
                st.rerun()

    # 4. 다음 블록 이동 버튼
    with p_cols[2 + PAGE_BLOCK_SIZE]:
        next_target = min(total_pages, block_end_page + 1)
        if st.button("다음 ▶", key="p_next", use_container_width=True, disabled=(block_end_page >= total_pages)):
            go_page(next_target)
            st.rerun()

    # 5. 맨 마지막 페이지 이동 버튼
    with p_cols[3 + PAGE_BLOCK_SIZE]:
        if st.button("마지막 »", key="p_last", use_container_width=True, disabled=(current_page == total_pages)):
            go_page(total_pages)
            st.rerun()