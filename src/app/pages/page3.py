import streamlit as st

col1, col2 = st.columns([8, 1])

with col2:
    if st.button("🏠 Home"):
        st.switch_page("pages/home.py")

import pandas as pd
import streamlit as st


# -----------------------------
# CSV 불러오기
# -----------------------------
@st.cache_data
def load_faq_data():
    df = pd.read_csv(
        "data/car_faq.csv",
        encoding="utf-8-sig",
    )

    # 질문과 답변의 앞뒤 공백 제거
    df["question"] = df["question"].astype(str).str.strip()
    df["answer"] = df["answer"].astype(str).str.strip()

    return df


faq_df = load_faq_data()


# -----------------------------
# 헤드라인
# -----------------------------
title_col, link_col, empty_col = st.columns([3, 3, 6])

with title_col:
    st.subheader("자동차 리콜센터 FAQ")

with link_col:
    st.link_button(
        "🚗 자동차 리콜센터 바로가기",
        "https://www.car.go.kr",
    )

st.write(
    "자동차 리콜 및 제작결함과 관련하여 "
    "자주 묻는 질문을 확인해 보세요."
)


# -----------------------------
# 자동차 리콜센터 FAQ 출력
# -----------------------------
for index, row in faq_df.iterrows():
    question = str(row["question"]).strip()
    answer = str(row["answer"]).strip()

    if question.startswith("Q.") or question.startswith("Q,"):
        toggle_title = question
    else:
        toggle_title = f"Q. {question}"

    answer = answer.replace(
        "www.car.go.kr",
        "[자동차리콜센터](https://www.car.go.kr)",
    )

    with st.expander(toggle_title):
        st.markdown(f"**A.** {answer}")