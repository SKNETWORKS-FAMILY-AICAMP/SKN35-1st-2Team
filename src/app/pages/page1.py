import streamlit as st

# ==============Home 버튼==============
col1, col2 = st.columns([8, 1])

with col2:
    if st.button("🏠 Home"):
        st.switch_page("pages/home.py")

st.title("🚗 자동차 리콜 분석")

# ============== Session State 초기화 ==============
if "tabs" not in st.session_state:
    st.session_state.tabs = []
    
# ============== 기업 선택 ==============
companies = ["현대", "기아", "BMW"]
selected_company = st.radio("기업 선택", companies,horizontal=True)

# ============== 탭 추가 ==============
if st.button("➕ 탭 추가"):
    # 중복 체크
    exist = any(tab["company"] == selected_company for tab in st.session_state.tabs)
    if exist:
        st.warning(f"'{selected_company}' 탭은 이미 열려 있습니다.")
    else:
        st.session_state.tabs.append({"company": selected_company, "start": 2012, "end": 2024, "graph": "기업별 리콜건수"})
        st.rerun()
st.divider()

# ============== 탭이 없을 때 ==============
if len(st.session_state.tabs) == 0:
    st.info("기업을 선택한 후 '➕ 탭 추가' 버튼을 눌러주세요.")

# ============== 탭 생성 ==============
else:
    tab_names = [tab["company"] for tab in st.session_state.tabs]
    tabs = st.tabs(tab_names)
    years = list(range(2000, 2026))

    # ============== 탭 내용 ==============
    for i, tab in enumerate(tabs):
         with tab:
            info = st.session_state.tabs[i]
            st.subheader(f"📊 {info['company']} 분석")

            # ============== 기간 선택 ==============
            col1, col2 = st.columns(2)
            with col1:
                info["start"] = st.selectbox("시작년도", years, index=years.index(info["start"]), key=f"start_{i}")

            with col2:
                info["end"] = st.selectbox("종료년도", years, index=years.index(info["end"]), key=f"end_{i}")

            # ============== 그래프 종류 선택 ==============
            info["graph"] = st.radio( "그래프 종류",["기업별 리콜건수","년도별 리콜건수","차종별 리콜건수","위험도"],horizontal=True,key=f"graph_{i}")
            st.divider()

            # ============== 그래프 출력 ==============
            st.write("### 📈 그래프 영역")
            st.info(f""" 기업 : {info['company']} 기간 : {info['start']} ~ {info['end']} 그래프 : {info['graph']} """)
            st.write("⬆️ 여기에 실제 그래프가 들어갑니다.")
            st.divider()

            # ============== 탭 삭제 ==============
            if st.button("🗑 탭 삭제",key=f"delete_{i}"):
                del st.session_state.tabs[i]
                st.rerun()