import os
import sys
import streamlit as st

# 1. 모듈 경로 설정: src 및 루트 디렉토리를 sys.path 최상단에 추가하여 DB 유틸리티 등 상위 모듈 접근 가능
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. DB 작성 유틸리티 함수 및 선택 옵션 (브랜드, 카테고리) 임포트
from src.db.news.db_utils import add_post, BRANDS, CATEGORIES

# Streamlit 페이지 설정
st.set_page_config(page_title="새 게시글 작성", page_icon="✏️", layout="wide")

# 3. 헤더 앵커 링크 아이콘 숨김 처리 커스텀 CSS
st.markdown(
    """
    <style>
    a.header-anchor {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 상단 내비게이션: 게시글 목록 페이지로 돌아가기
if st.button("← 목록으로 가기"):
    st.switch_page("pages/community.py")

st.title("✏️ 새 게시글 작성")

# 4. 게시글 등록 폼(Form) 구성 (clear_on_submit=True: 등록 완료 시 입력 폼 초기화)
with st.form("write_form", clear_on_submit=True):
    # 4-1. 필수 항목: 제목 입력
    title = st.text_input("제목 *")
    
    # 4-2. 3컬럼 레이아웃 (브랜드 선택, 모델명 입력, 카테고리 선택)
    col1, col2, col3 = st.columns(3)
    with col1:
        brand = st.selectbox("브랜드", BRANDS)
    with col2:
        model = st.text_input("모델명 (예: 아반떼 CN7)")
    with col3:
        category = st.selectbox("카테고리", CATEGORIES)
    
    # 4-3. 2컬럼 레이아웃 (작성자 닉네임, 수정/삭제용 비밀번호)
    col_author, col_pw = st.columns(2)
    with col_author:
        author = st.text_input("작성자 닉네임", value="익명")
    with col_pw:
        password = st.text_input("비밀번호 (수정/삭제용) *", type="password", placeholder="수정 및 삭제 시 사용할 비밀번호")

    # 4-4. 필수 항목: 본문 내용 입력
    content = st.text_area(
        "내용 *", height=220,
        placeholder="리콜 경험, 증상, 정비소 대응, 궁금한 점 등을 자유롭게 적어주세요.",
    )

    # 폼 제출 버튼
    submitted = st.form_submit_button("게시글 등록", type="primary", use_container_width=True)
    
    # 5. 제출 클릭 시 입률 데이터 유효성 검증 및 DB 데이터 적재
    if submitted:
        # 5-1. 필수 항목 (제목, 내용, 비밀번호) 누락 여부 검증
        if not title.strip() or not content.strip() or not password.strip():
            st.error("제목, 내용, 비밀번호는 필수 입력 항목입니다.")
        # 5-2. DB에 게시글 등록 (add_post) 후 게시글 목록으로 페이지 이동
        else:
            add_post(title.strip(), content.strip(), brand, model.strip(), category, author.strip() or "익명", password.strip())
            st.success("게시글이 등록되었습니다!")
            st.switch_page("pages/community.py")
