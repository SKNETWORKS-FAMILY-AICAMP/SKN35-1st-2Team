import os
import sys
import streamlit as st

# 1. 모듈 경로 설정: src 및 루트 디렉토리를 sys.path 최상단에 추가하여 상위 모듈 접근 가능
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. 모듈 핫 리로드 (db_utils 변경 사항 실시간 반영)
import importlib
import src.db.news.db_utils
importlib.reload(src.db.news.db_utils)

from src.db.news.db_utils import (
    get_post, like_post, unlike_post, get_comments, add_comment, increment_views,
    verify_comment_password, update_comment, delete_comment, verify_post_password, delete_post
)

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="게시글 상세", page_icon="📖", layout="wide")

# 3. 세션 상태(st.session_state)에서 전달된 상세 게시글 ID 검증
post_id = st.session_state.get("detail_post_id")

if not post_id:
    st.warning("선택된 게시글이 없습니다. 목록 페이지에서 게시글을 선택해 주세요.")
    st.stop()

# 4. 세션 상태를 활용한 조회수(Views) 1회성 증가 로직 (동일 세션 내 새로고침 시 중복 조회수 증가 방지)
viewed_posts = st.session_state.setdefault("viewed_posts", set())
if post_id not in viewed_posts:
    increment_views(post_id)
    viewed_posts.add(post_id)

# 5. DB에서 상세 게시글 데이터 조회 및 존재 여부 확인
post = get_post(post_id)

if not post:
    st.error("존재하지 않거나 삭제된 게시글입니다.")
    st.stop()

# 6. 상단 내비게이션 및 게시글 컨트롤 버튼 (목록 가기, 수정하기, 삭제하기)
col_back, _, col_edit, col_del = st.columns([1, 4.2, 1, 1])
with col_back:
    if st.button("← 목록으로 가기", use_container_width=True):
        st.switch_page("pages/community.py")

with col_edit:
    if st.button("✏️ 수정하기", use_container_width=True):
        st.session_state["edit_post_id"] = post["id"]
        st.switch_page("pages/edit_page.py")

with col_del:
    if st.button("🗑️ 삭제하기", use_container_width=True):
        # 삭제 확인 모달/컨테이너 토글 상태 변경
        st.session_state["show_delete_modal"] = not st.session_state.get("show_delete_modal", False)
        st.rerun()

# 7. 게시글 삭제 확인 팝업/모달 영역 (비밀번호 일치 검증 후 삭제 실행)
if st.session_state.get("show_delete_modal"):
    with st.container(border=True):
        st.warning("⚠️ 정말 이 게시글을 삭제하시겠습니까?")
        with st.form("post_delete_confirm_form"):
            del_pwd = st.text_input("게시글 비밀번호", type="password", placeholder="글 작성 시 설정한 비밀번호 입력 (기본값: 1234)")
            c_yes, c_no = st.columns([1, 1])
            with c_yes:
                submit_del = st.form_submit_button("네, 삭제합니다", type="primary", use_container_width=True)
            with c_no:
                cancel_del = st.form_submit_button("아니오 (취소)", use_container_width=True)

            if submit_del:
                # 작성 시 비밀번호 일치 여부 확인
                if verify_post_password(post["id"], del_pwd):
                    delete_post(post["id"])
                    st.session_state.pop("show_delete_modal", None)
                    st.session_state.pop("detail_post_id", None)
                    st.success("삭제가 완료되었습니다!")
                    st.switch_page("pages/community.py")
                else:
                    st.error("비밀번호가 일치하지 않습니다.")

            if cancel_del:
                st.session_state.pop("show_delete_modal", None)
                st.rerun()

st.divider()

# 8. 브랜드 및 카테고리 태그 뱃지 UI 렌더링
brand_html = f'<span style="background-color: #e7f5ff; color: #1c7ed6; padding: 4px 12px; border-radius: 14px; font-size: 13px; font-weight: 600; margin-right: 6px;">{post["brand"] or "기타"}</span>'
cat_html = f'<span style="background-color: #f1f3f5; color: #495057; padding: 4px 12px; border-radius: 14px; font-size: 13px; font-weight: 600;">{post["category"] or "기타"}</span>'
st.markdown(f"{brand_html}{cat_html}", unsafe_allow_html=True)

# 9. 게시글 제목 및 주요 메타정보 (모델, 작성자, 작성일시, 조회수)
st.markdown(f"# {post['title']}")
model_txt = f"모델: **{post['model']}**  |  " if post["model"] else ""
views_count = post.get("views") or 0
st.caption(f"{model_txt}작성자: **{post['author'] or '익명'}**  |  작성일: {post['created_at']}  |  👁️ 조회수: **{views_count}회**")

st.divider()

# 10. 게시글 본문 내용 박스 렌더링
st.markdown(
    f"""
    <div style="font-size: 16px; line-height: 1.8; min-height: 150px; background-color: #fafafa; padding: 22px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 15px;">
        {post['content']}
    </div>
    """,
    unsafe_allow_html=True,
)

# 11. 공감(좋아요) 토글 버튼 처리 (세션 내 토글 상태에 따라 like_post / unlike_post 실행)
st.markdown("<br>", unsafe_allow_html=True)

liked_posts = st.session_state.setdefault("liked_posts", set())
is_liked = post["id"] in liked_posts

_, like_col, _ = st.columns([2.5, 2, 2.5])
with like_col:
    btn_label = f"❤️ 공감 취소 ({post['likes']})" if is_liked else f"👍 공감하기 ({post['likes']})"
    btn_type = "primary" if is_liked else "secondary"
    if st.button(btn_label, type=btn_type, use_container_width=True):
        if is_liked:
            unlike_post(post["id"])
            liked_posts.remove(post["id"])
        else:
            like_post(post["id"])
            liked_posts.add(post["id"])
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.markdown("<br>", unsafe_allow_html=True)

# 12. 댓글 세션: 등록된 댓글 목록 조회 및 인라인 수정/삭제 인터페이스
comments = get_comments(post["id"])
st.markdown(f"### 💬 댓글 ({len(comments)}개)")

if not comments:
    st.caption("아직 작성된 댓글이 없습니다. 첫 댓글을 남겨보세요!")
else:
    for c in comments:
        # 각 댓글별 수정/삭제 세션 플래그 확인
        is_editing = st.session_state.get(f"editing_c_{c['id']}")
        is_deleting = st.session_state.get(f"deleting_c_{c['id']}")

        with st.container(border=True):
            if is_editing:
                # 12-1. 인라인 댓글 수정 모드 폼
                st.markdown(f"✏️ **{c['author'] or '익명'}님의 댓글 수정**")
                with st.form(key=f"form_c_edit_{c['id']}"):
                    new_content = st.text_area("수정할 내용", value=c["content"], height=85)
                    edit_pwd = st.text_input("댓글 비밀번호", type="password", key=f"pwd_edit_{c['id']}", placeholder="작성 시 설정한 비밀번호 입력")
                    e_sub1, e_sub2, _ = st.columns([1, 1, 2.5])
                    with e_sub1:
                        if st.form_submit_button("수정 완료", type="primary", use_container_width=True):
                            if not edit_pwd.strip():
                                st.error("비밀번호를 입력해 주세요.")
                            elif verify_comment_password(c["id"], edit_pwd.strip()):
                                update_comment(c["id"], new_content.strip())
                                st.session_state.pop(f"editing_c_{c['id']}", None)
                                st.success("댓글이 수정되었습니다.")
                                st.rerun()
                            else:
                                st.error("비밀번호가 일치하지 않습니다.")
                    with e_sub2:
                        if st.form_submit_button("취소", use_container_width=True):
                            st.session_state.pop(f"editing_c_{c['id']}", None)
                            st.rerun()

            elif is_deleting:
                # 12-2. 인라인 댓글 삭제 확인 모드 폼
                st.markdown(f"🗑️ **{c['author'] or '익명'}님의 댓글 삭제**")
                with st.form(key=f"form_c_del_{c['id']}"):
                    del_pwd = st.text_input("댓글 비밀번호 확인", type="password", key=f"pwd_del_{c['id']}", placeholder="작성 시 설정한 비밀번호 입력")
                    d_sub1, d_sub2, _ = st.columns([1, 1, 2.5])
                    with d_sub1:
                        if st.form_submit_button("삭제 실행", type="primary", use_container_width=True):
                            if not del_pwd.strip():
                                st.error("비밀번호를 입력해 주세요.")
                            elif verify_comment_password(c["id"], del_pwd.strip()):
                                delete_comment(c["id"])
                                st.session_state.pop(f"deleting_c_{c['id']}", None)
                                st.success("댓글이 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("비밀번호가 일치하지 않습니다.")
                    with d_sub2:
                        if st.form_submit_button("취소", use_container_width=True):
                            st.session_state.pop(f"deleting_c_{c['id']}", None)
                            st.rerun()

            else:
                # 12-3. 일반 댓글 표출 카드 (작성자, 작성시간, 내용 및 수정/삭제 버튼)
                col_info, col_actions = st.columns([4, 1.2])
                with col_info:
                    edited_tag = ' <span style="color: #868e96; font-size: 11px; font-weight: 600;">(수정됨)</span>' if c.get("updated_at") else ''
                    st.markdown(f"**{c['author'] or '익명'}**  <span style='color: gray; font-size: 12px;'>({c['created_at']})</span>{edited_tag}", unsafe_allow_html=True)
                    st.write(c["content"])
                with col_actions:
                    act_c1, act_c2 = st.columns(2)
                    with act_c1:
                        if st.button("수정", key=f"c_edit_btn_{c['id']}", use_container_width=True):
                            st.session_state[f"editing_c_{c['id']}"] = True
                            st.session_state.pop(f"deleting_c_{c['id']}", None)
                            st.rerun()
                    with act_c2:
                        if st.button("삭제", key=f"c_del_btn_{c['id']}", use_container_width=True):
                            st.session_state[f"deleting_c_{c['id']}"] = True
                            st.session_state.pop(f"editing_c_{c['id']}", None)
                            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 13. 하단 신규 댓글 작성 폼 (add_comment)
with st.form("detail_comment_form", clear_on_submit=True):
    st.markdown("#### ✏️ 댓글 작성")
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    with c1:
        c_author = st.text_input("닉네임", value="익명")
    with c2:
        c_password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", help="수정/삭제 시 필요합니다")

    c_content = st.text_area("댓글 내용", height=90, placeholder="매너 있는 댓글을 작성해주세요.")

    submitted = st.form_submit_button("댓글 등록하기", type="primary")
    if submitted:
        if not c_content.strip():
            st.error("댓글 내용을 입력해 주세요.")
        elif not c_password.strip():
            st.error("댓글 비밀번호를 입력해 주세요.")
        else:
            add_comment(post["id"], c_author.strip() or "익명", c_content.strip(), c_password.strip())
            st.success("댓글이 등록되었습니다.")
            st.rerun()

