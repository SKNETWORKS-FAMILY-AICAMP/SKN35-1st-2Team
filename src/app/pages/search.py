import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="자동차 리콜 검색", layout="wide")
st.title("🚗 자동차 리콜·결함 정보 검색")

# DB_PATH = os.path.join(os.path.dirname(__file__), "..", "recall.db")

# @st.cache_resource
# def get_connection():
#     return sqlite3.connect(DB_PATH, check_same_thread=False)

# @st.cache_data
# def get_manufacturers():
#     conn = get_connection()
#     df = pd.read_sql_query("SELECT DISTINCT manufacturer FROM recalls ORDER BY manufacturer", conn)
#     return df["manufacturer"].tolist()

# @st.cache_data
# def get_models(manufacturer=None):
#     conn = get_connection()
#     if manufacturer and manufacturer != "전체":
#         query = "SELECT DISTINCT model_name FROM recalls WHERE manufacturer = ? ORDER BY model_name"
#         df = pd.read_sql_query(query, conn, params=[manufacturer])
#     else:
#         df = pd.read_sql_query("SELECT DISTINCT model_name FROM recalls ORDER BY model_name", conn)
#     return df["model_name"].tolist()

# def search_recalls(manufacturer=None, model=None, keyword=None):
#     conn = get_connection()
#     query = "SELECT * FROM recalls WHERE 1=1"
#     params = []

#     if manufacturer and manufacturer != "전체":
#         query += " AND manufacturer = ?"
#         params.append(manufacturer)
#     if model and model != "전체":
#         query += " AND model_name = ?"
#         params.append(model)
#     if keyword:
#         query += " AND (defect_type LIKE ? OR defect_detail LIKE ?)"
#         params.extend([f"%{keyword}%", f"%{keyword}%"])

#     query += " ORDER BY recall_date DESC"
#     return pd.read_sql_query(query, conn, params=params)


st.subheader("🔎 조건 검색")

col1, col2, col3 = st.columns([1, 1, 1.4])

with col1:
    # manufacturer_list = ["전체"] + get_manufacturers()
    manufacturer_list = ["전체","비엠더블유","폭스바겐","현대자동차","기아"]
    manufacturer = st.selectbox("기업(브랜드)", manufacturer_list)

with col2:
    # model_list = ["전체"] + get_models(manufacturer)
    # model_list = ["검색"]
    # model = st.selectbox("차종", model_list)
        keyword = st.text_input("차종", placeholder="검색란")


with col3:
    keyword = st.text_input("결함 키워드 (선택)", placeholder="예: 브레이크, 엔진, 에어백")

search_clicked = st.button("🔍 검색", use_container_width=True, type="primary")

# if search_clicked:
#     st.session_state.results = search_recalls(manufacturer, model, keyword)

# if "results" not in st.session_state:
#     st.session_state.results = search_recalls()

# df = st.session_state.results

# st.divider()
# st.subheader("📊 리콜 건수 조회")

# m1, m2, m3 = st.columns(3)
# m1.metric("검색된 리콜 건수", f"{len(df)}건")
# m2.metric("대상 브랜드 수", df["manufacturer"].nunique() if len(df) > 0 else 0)
# m3.metric("대상 차종 수", df["model_name"].nunique() if len(df) > 0 else 0)

st.divider()
st.subheader("📋 리콜 목록")

# if len(df) == 0:
#     st.warning("검색 조건에 맞는 리콜 정보가 없습니다.")
# else:
#     for idx, row in df.iterrows():
#         with st.container(border=True):
#             c1, c2 = st.columns([5, 1])
#             with c1:
#                 st.markdown(f"**[{row['manufacturer']}] {row['model_name']}** - {row['defect_type']}")
#                 st.caption(f"📅 {row['recall_date']}")
#             with c2:
#                 if st.button("상세보기", key=f"detail_{idx}"):
#                     st.session_state.selected_id = idx

#     if "selected_id" in st.session_state and st.session_state.selected_id in df.index:
#         st.divider()
#         st.subheader("📄 상세 정보")

#         row = df.loc[st.session_state.selected_id]

#         with st.container(border=True):
#             c1, c2 = st.columns(2)
#             with c1:
#                 st.markdown(f"**제작사**: {row['manufacturer']}")
#                 st.markdown(f"**차종**: {row['model_name']}")
#                 st.markdown(f"**리콜일자**: {row['recall_date']}")
#             with c2:
#                 st.markdown(f"**결함 유형**: {row['defect_type']}")
#                 if row.get("affected_count") is not None:
#                     st.markdown(f"**대상 대수**: {row['affected_count']:,}대")

#             st.markdown("**결함 상세 내용**")
#             st.write(row["defect_detail"])

#             if row.get("source_url"):
#                 st.markdown(f"[원본 리콜 공고 보기]({row['source_url']})")