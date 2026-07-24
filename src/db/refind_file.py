import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "recall_data_en.csv"
OUTPUT_PATH = BASE_DIR / "data" / "recall_data.csv"

# CSV 읽기
df = pd.read_csv(DATA_PATH)

# 원하는 제조사 목록
target_manufacturers = [
    "벤츠",
    "현대자동차",
    "기아",
    "비엠더블유",
    "폭스바겐그룹"
]

# manufacturer 컬럼 기준 필터링
filtered_df = df[df["manufacturer"].isin(target_manufacturers)]

# CSV 저장
filtered_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"저장 완료: {OUTPUT_PATH}")
print(f"총 {len(filtered_df)}개 데이터")