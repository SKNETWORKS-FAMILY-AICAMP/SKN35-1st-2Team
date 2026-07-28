import os
import sys
import streamlit as st

# 1. 모듈 경로 설정: src 및 루트 디렉토리를 sys.path 최상단에 추가하여 상위 모듈(db 등) 접근 가능하도록 설정
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. DB 조작 함수 및 카테고리/브랜드 데이터 유틸리티 모듈 임포트
from src.db.news.db_utils import get_post, update_post, delete_post, verify_post_password, BRANDS, CATEGORIES

# Streamlit 페이지 기본 레이아웃 및 타이틀 설정
st.set_page_config(page_title="게시글 수정", page_icon="🛠️", layout="wide")

# 상단 내비게이션: 목록 페이지로 돌아가기
if st.button("← 목록으로 가기"):
    st.switch_page("pages/community.py")

st.title("🛠️ 게시글 수정")

# 3. 세션 상태(session_state)에서 수정 대상 게시글 ID 추출 및 유효성 검증
post_id = st.session_state.get("edit_post_id")

# 3-1. 전달받은 게시글 ID가 없는 경우 접근 차단 (목록 페이지를 통한 정상 접근 유도)
if not post_id:
    st.warning("수정할 게시글이 선택되지 않았습니다. 목록 페이지에서 '수정' 버튼을 눌러 접근해 주세요.")
    st.stop()

# 3-2. DB에서 대상 게시글 상세 정보 조회
post = get_post(post_id)

# 3-3. 해당 게시글이 DB에 존재하지 않는 경우 예외 처리
if post is None:
    st.warning("존재하지 않는 게시글입니다.")
    st.stop()

# 4. 게시글 수정 폼(Form) 생성: 기존 DB 데이터를 입력 폼 기본값으로 바인딩
with st.form("edit_form"):
    # 4-1. 기존 제목 설정
    title = st.text_input("제목 *", value=post["title"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # 4-2. 기존 브랜드 선택값 바인딩 (목록에 없을 경우 0번 인덱스 기본 지정)
        brand = st.selectbox("브랜드", BRANDS, index=BRANDS.index(post["brand"]) if post["brand"] in BRANDS else 0)
    with col2:
        # 4-3. 기존 모델명 설정
        model = st.text_input("모델명", value=post["model"] or "")
    with col3:
        # 4-4. 기존 카테고리 선택값 바인딩
        category = st.selectbox(
            "카테고리", CATEGORIES,
            index=CATEGORIES.index(post["category"]) if post["category"] in CATEGORIES else 0,
        )
    
    # 4-5. 기존 게시글 본문 내용 바인딩
    content = st.text_area("내용 *", value=post["content"], height=220)
    
    # 4-6. 수정 권한 확인용 비밀번호 입력란
    password_input = st.text_input("비밀번호 확인 *", type="password", placeholder="게시글 작성 시 등록한 비밀번호를 입력하세요.")

    # 폼 제출 버튼
    submitted = st.form_submit_button("수정 완료", type="primary", use_container_width=True)

    # 5. 수정 폼 제출 시 유효성 검증 및 DB 업데이트 처리
    if submitted:
        # 5-1. 필수 입력 항목(제목, 내용) 공백 여부 검증
        if not title.strip() or not content.strip():
            st.error("제목과 내용은 필수 입력 항목입니다.")
        # 5-2. 비밀번호 입력 여부 확인
        elif not password_input.strip():
            st.error("수정하려면 작성 시 입력한 비밀번호를 입력해야 합니다.")
        # 5-3. DB에 저장된 비밀번호 일치 여부 검증
        elif not verify_post_password(post_id, password_input.strip()):
            st.error("비밀번호가 일치하지 않습니다.")
        # 5-4. 검증 성공 시 DB 업데이트 실행 및 이동
        else:
            # DB 레코드 업데이트
            update_post(post_id, title.strip(), content.strip(), brand, model.strip(), category)
            st.success("게시글이 수정되었습니다!")
            
            # 사용 후 수정 세션 변수 삭제 및 커뮤니티 목록으로 이탈
            del st.session_state["edit_post_id"]
            st.switch_page("pages/community.py")
