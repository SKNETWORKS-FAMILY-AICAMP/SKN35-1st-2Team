import os
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_DATABASE')}?charset=utf8mb4",
        pool_pre_ping=True
    )