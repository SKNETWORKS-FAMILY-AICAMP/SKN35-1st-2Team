import streamlit as st

col1, col2 = st.columns([8, 1])

with col2:
    if st.button("🏠 Home"):
        st.switch_page("pages/home.py")

st.title("페이지3")
