import pandas as pd
from pathlib import Path

from src.db.engine import get_engine

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_PATH = BASE_DIR / "crawled" / "news" / "recall_news_news_schema.csv"


def seed_news_data():
    """
    CSV를 news 테이블에 적재
    (최초 1회만 직접 실행)
    """
    df = pd.read_csv(DATA_PATH)
    engine = get_engine()
    df.to_sql(
        name="news",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"{len(df)}건 적재 완료")


if __name__ == "__main__":
    seed_news_data()