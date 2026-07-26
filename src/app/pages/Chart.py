import streamlit as st

# db 모듈을 import하기 위해 프로젝트 루트 경로를 sys.path에 추가
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from db.refind_data import get_yearly_recall, get_car_model_recall, get_risk_trend

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
companies = ["현대", "기아", "BMW", "벤츠" , "폭스바겐"]
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
    years = list(range(2000, 2025))

    # ============== 탭 내용 ==============
    for i, tab in enumerate(tabs):
         with tab:
            info = st.session_state.tabs[i]
            st.subheader(f"📊 {info['company']} 분석")

            # ============== 그래프 종류 선택 ==============
            info["graph"] = st.radio( "그래프 종류",["년도별 리콜건수","차종별 리콜건수","위험도"],horizontal=True,key=f"graph_{i}")
            st.divider()

            # ============== 기간 선택 ==============
            if info["graph"] != "위험도":

                with st.form(key=f"period_form_{i}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        start = st.selectbox( "시작년도", years,index=years.index(info["start"]))

                    with col2:
                        end = st.selectbox("종료년도", years, index=years.index(info["end"]))

                    apply = st.form_submit_button("적용")

                    if apply:
                        info["start"] = start
                        info["end"] = end
                        st.rerun()

            st.divider()
            # ============== 그래프 출력 ==============
            st.write("### 📈 그래프 영역")
            if info["graph"] == "년도별 리콜건수":
                st.info(f"기업 : {info['company']} | 기간 : {info['start']} ~ {info['end']}")
                chart_df = get_yearly_recall(info["company"], info["start"], info["end"])
                if chart_df.empty:
                    st.warning("해당 조건에 데이터가 없습니다.")
                else:
                    st.line_chart(chart_df, y="리콜건수")

            elif info["graph"] == "차종별 리콜건수":
                st.info(f"기업 : {info['company']} | 기간 : {info['start']} ~ {info['end']}")
                chart_df = get_car_model_recall(info["company"], info["start"], info["end"])
                if chart_df.empty:
                    st.warning("해당 조건에 데이터가 없습니다.")
                else:
                    st.bar_chart(chart_df, y="리콜건수")

            elif info["graph"] == "위험도":
                st.info(f"기업 : {info['company']} | 최근 3년 추세")
                chart_df = get_risk_trend(info["company"])
                if chart_df.empty:
                    st.warning("최근 3년 데이터가 없습니다.")
                else:
                    st.line_chart(chart_df, y="리콜건수")
                    if len(chart_df) >= 2:
                        latest = chart_df["리콜건수"].iloc[-1]
                        prev = chart_df["리콜건수"].iloc[-2]
                        diff = latest - prev
                        trend = "📈 증가" if diff > 0 else ("📉 감소" if diff < 0 else "➡ 유지")
                        st.metric(f"{chart_df.index[-1]}년 전년 대비", f"{latest}건", delta=f"{diff} ({trend})")

            st.divider()
            
            # ============== 탭 삭제 ==============
            if st.button("🗑 탭 삭제",key=f"delete_{i}"):
                del st.session_state.tabs[i]
                st.rerun()