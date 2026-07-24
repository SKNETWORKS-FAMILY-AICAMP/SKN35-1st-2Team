import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "recall_data.csv"

load_dotenv()

engine = create_engine(
    f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}?charset=utf8mb4"
)

df = pd.read_csv(DATA_PATH)

df.to_sql(
    name="car_recall",
    con=engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000,
)

