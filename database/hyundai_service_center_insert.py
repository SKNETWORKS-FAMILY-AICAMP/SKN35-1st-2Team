import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}?charset=utf8mb4"
)

df = pd.read_csv("crawled/hyundai_service_centers.csv")

mask = df["latitude"] > 90

temp = df.loc[mask, "latitude"].copy()
df.loc[mask, "latitude"] = df.loc[mask, "longitude"]
df.loc[mask, "longitude"] = temp

print(df.iloc[1])

df.to_sql(
    name="hyundai_service_center",
    con=engine,
    if_exists="append",  # 기존 데이터 유지하고 추가
    index=False,
    method="multi",  # 여러 건을 한 번에 INSERT
    chunksize=1000,  # 1000건씩 나누어 INSERT
)
