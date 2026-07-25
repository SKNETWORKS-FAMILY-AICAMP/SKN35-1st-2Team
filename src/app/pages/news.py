import streamlit as st

# =============================================================================
# ⚠️ 사전 준비 사항 (crawlers 연동 전 임시 안내)
# -----------------------------------------------------------------------------
# 이 페이지는 크롤러가 수집한 뉴스 데이터가 아래 형태로 DB(news 테이블 등)에
# 저장되어 있고, db/db_utils.py 에 다음 두 함수가 구현되어 있다고 가정합니다.
#
#   def get_news(keyword: str, sort_by: str) -> list[dict]:
#       """
#       조건에 맞는 리콜 뉴스 목록을 반환.
#       각 dict는 아래 키를 포함해야 함:
#         - id            : 고유 ID
#         - title         : 뉴스 제목
#         - summary       : 요약/본문 일부
#         - url           : 원문 링크
#         - source        : 언론사/매체명
#         - published_at  : 게시일 (문자열 또는 datetime)
#       sort_by는 "최신순" 또는 "관련도순" 중 하나.
#       """
#
#   def count_news(keyword: str = "") -> int:
#       """조건에 맞는 리콜 뉴스 총 건수를 반환."""
# =============================================================================

# 개발 중 DB 연동 전에 화면만 미리 보고 싶다면 True로 변경
USE_DUMMY_DATA = True


# 1. 페이지 기본 설정
st.set_page_config(page_title="소식", page_icon="📰", layout="wide")


# 2. 상단 헤더
st.title("📰소식")
st.write("자동차 리콜·결함 관련 최신 뉴스를 한눈에 확인해 보세요.")

# 3. 검색 필터 세션 상태 초기화
NEWS_SEARCH_DEFAULTS = {
    "news_keyword": "",
    "news_sort": "최신순",
}
for k, v in NEWS_SEARCH_DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reset_news_filters():
    for k, v in NEWS_SEARCH_DEFAULTS.items():
        st.session_state[k] = v


# 4. 검색 폼
with st.form("news_search_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("검색어", placeholder="제목, 요약 내용으로 검색", key="news_keyword")
    with col2:
        st.selectbox("정렬", ["최신순", "관련도순"], key="news_sort")

    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    with btn_col1:
        st.form_submit_button("🔍 검색", type="primary", use_container_width=True)
    with btn_col2:
        st.form_submit_button("초기화", use_container_width=True, on_click=reset_news_filters)


# 5. 현재 검색 조건 변수 할당
keyword = st.session_state["news_keyword"]
sort_by = st.session_state["news_sort"]

st.divider()


# 6. 데이터 조회 (더미 데이터 or 실제 DB)
def _get_dummy_news():
    dummy = [
        {
            "id": 1,
            "title": "○○자동차, 브레이크 결함으로 12만대 리콜",
            "summary": "국토교통부는 ○○자동차의 일부 차종에서 브레이크 오일 누유 결함이 발견되어 리콜을 실시한다고 밝혔다.",
            "url": "https://example.com/news/1",
            "source": "예시일보",
            "published_at": "2026-07-20",
        },
        {
            "id": 2,
            "title": "△△모터스, 에어백 센서 오작동 관련 자발적 리콜 발표",
            "summary": "△△모터스는 에어백 센서 오작동 가능성이 확인되어 관련 차종에 대해 자발적 리콜을 진행한다고 발표했다.",
            "url": "https://example.com/news/2",
            "source": "예시타임즈",
            "published_at": "2026-07-18",
        },
    ]
    return dummy


if USE_DUMMY_DATA:
    news_list = _get_dummy_news()
    total_count = len(news_list)
else:
    news_list = get_news(keyword, sort_by)
    total_count = count_news(keyword)

# 7. 검색 결과 건수 표시
active_filters = bool(keyword.strip())
if active_filters:
    st.caption(f"🔎 검색 결과: **{total_count}건**")
else:
    st.caption(f"전체 리콜 뉴스: **{total_count}건**")


# 8. 뉴스 렌더링 영역
if not news_list:
    st.info(
        "검색 결과가 없습니다. 검색어를 변경해 보세요."
        if active_filters
        else "아직 등록된 리콜 뉴스가 없습니다."
    )
else:
    for news in news_list:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"### {news['title']}")
            with c2:
                st.caption(f"📰 {news['source'] or '출처 미상'}")

            st.caption(f"게시일: {news['published_at']}")

            with st.expander("요약 보기"):
                st.write(news["summary"] or "요약 정보가 없습니다.")
                st.link_button("🔗 원문 보기", news["url"], use_container_width=False)