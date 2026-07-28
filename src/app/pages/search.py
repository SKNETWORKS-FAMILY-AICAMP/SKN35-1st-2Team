import streamlit as st
import pandas as pd

st.set_page_config(page_title="자동차 리콜·결함 안전등급 대시보드", layout="wide")

# ---------------------------
# 샘플 데이터 (나중에 DB로 교체 예정)
# ---------------------------
data = [
    {"manufacturer": "현대자동차", "car_model": "그랜저 IG", "recall_date": "2023-05-10",
     "defect_category": "엔진", "defect_detail": "엔진 내부 부품 결함으로 시동 꺼짐 발생 가능",
     "safety_grade": "B", "affected_count": 12500, "status": "완료"},
    {"manufacturer": "현대자동차", "car_model": "아반떼 CN7", "recall_date": "2024-01-22",
     "defect_category": "브레이크", "defect_detail": "브레이크 오일 누유로 제동력 저하 가능성",
     "safety_grade": "A", "affected_count": 8300, "status": "진행중"},
    {"manufacturer": "현대자동차", "car_model": "쏘나타 DN8", "recall_date": "2022-11-03",
     "defect_category": "전기장치", "defect_detail": "배터리 센서 오작동으로 방전 위험",
     "safety_grade": "C", "affected_count": 4200, "status": "완료"},

    {"manufacturer": "기아자동차", "car_model": "K5", "recall_date": "2023-08-15",
     "defect_category": "에어백", "defect_detail": "조수석 에어백 전개 오류 가능성",
     "safety_grade": "A", "affected_count": 15600, "status": "진행중"},
    {"manufacturer": "기아자동차", "car_model": "쏘렌토 MQ4", "recall_date": "2024-03-01",
     "defect_category": "엔진", "defect_detail": "엔진룸 배선 손상으로 화재 위험",
     "safety_grade": "A", "affected_count": 9800, "status": "진행중"},
    {"manufacturer": "기아자동차", "car_model": "셀토스", "recall_date": "2022-06-19",
     "defect_category": "조향장치", "defect_detail": "조향축 결합 불량으로 조작감 이상",
     "safety_grade": "B", "affected_count": 3100, "status": "완료"},

    {"manufacturer": "BMW", "car_model": "3시리즈", "recall_date": "2023-02-14",
     "defect_category": "엔진", "defect_detail": "연료 펌프 결함으로 시동 꺼짐 위험",
     "safety_grade": "B", "affected_count": 2200, "status": "완료"},
    {"manufacturer": "BMW", "car_model": "5시리즈", "recall_date": "2024-05-07",
     "defect_category": "전기장치", "defect_detail": "배터리 관리 시스템 소프트웨어 오류",
     "safety_grade": "C", "affected_count": 1500, "status": "진행중"},
    {"manufacturer": "BMW", "car_model": "X5", "recall_date": "2023-11-30",
     "defect_category": "브레이크", "defect_detail": "브레이크 부스터 결함으로 제동거리 증가",
     "safety_grade": "A", "affected_count": 900, "status": "완료"},
]

df_all = pd.DataFrame(data)

# ---------------------------
# 화면 구성
# ---------------------------
st.title("🚗 자동차 리콜·결함 안전등급 대시보드")
st.caption("차종 · 기업 · 결함 안전등급을 검색해보세요")

st.divider()

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    car_model_input = st.selectbox(
        "차종",
        ["전체"] + sorted(df_all["car_model"].unique().tolist())
    )

with col2:
    manufacturer_input = st.selectbox(
        "기업(제작사)",
        ["전체"] + sorted(df_all["manufacturer"].unique().tolist())
    )

with col3:
    grade_input = st.selectbox("안전등급", ["전체"] + sorted(df_all["safety_grade"].unique().tolist()))

search_btn = st.button("🔍 검색", use_container_width=True)

st.divider()

# ---------------------------
# 검색 로직
# ---------------------------
def filter_data(df, car_model, manufacturer, grade):
    result = df.copy()
    if car_model != "전체":
        result = result[result["car_model"] == car_model]
    if manufacturer != "전체":
        result = result[result["manufacturer"] == manufacturer]
    if grade != "전체":
        result = result[result["safety_grade"] == grade]
    return result

if search_btn:
    st.session_state["filtered"] = filter_data(df_all, car_model_input, manufacturer_input, grade_input)
elif "filtered" not in st.session_state:
    st.session_state["filtered"] = df_all  # 처음엔 전체 데이터 표시

df_result = st.session_state["filtered"]

st.subheader(f"검색 결과 ({len(df_result)}건)")

if df_result.empty:
    st.warning("검색 결과가 없습니다. 조건을 다시 확인해주세요.")
else:
    st.dataframe(
        df_result[["manufacturer", "car_model", "recall_date", "defect_category", "safety_grade", "affected_count", "status"]]
        .rename(columns={
            "manufacturer": "제작사", "car_model": "차종", "recall_date": "리콜일자",
            "defect_category": "결함부위", "safety_grade": "안전등급",
            "affected_count": "대상대수", "status": "진행상태"
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ---------------------------
    # 상세 조회
    # ---------------------------
    st.subheader("📋 상세 조회")
    selected_model = st.selectbox("상세히 볼 차종 선택", df_result["car_model"].unique(), key="detail_select")
    detail = df_result[df_result["car_model"] == selected_model].iloc[0]

    c1, c2 = st.columns(2)
    with c1:
        st.metric("제작사", detail["manufacturer"])
        st.metric("안전등급", detail["safety_grade"])
        st.metric("진행상태", detail["status"])
    with c2:
        st.metric("리콜 대상 대수", f"{detail['affected_count']:,}대")
        st.metric("리콜일자", detail["recall_date"])
        st.metric("결함부위", detail["defect_category"])

    st.write("**결함 상세 내용**")
    st.info(detail["defect_detail"])
    