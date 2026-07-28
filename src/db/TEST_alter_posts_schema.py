"""
[1회성 DB 스키마 마이그레이션 스크립트]
posts 테이블에서 레거시 컬럼(brand, model)을 제거하고
ERD DDL 스키마(manufacturer_id, car_model_id)로 컬럼 구조를 완전 동기화합니다.
파일명 규칙에 따라 'TEST'를 포함합니다.
"""

import os
import sys
from pathlib import Path

# src 디렉토리를 sys.path 최상단에 추가
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from db.db_utils import init_db, get_conn, get_or_create_manufacturer, get_or_create_car_model


def alter_posts_schema():
    print("1. DB 기본 테이블 및 시딩 상태 확인...")
    init_db()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    print("2. 기존 brand/model 문자열 데이터를 manufacturer_id/car_model_id로 마이그레이션...")
    try:
        cur.execute("SHOW COLUMNS FROM posts LIKE 'brand'")
        has_brand = cur.fetchone()
        
        if has_brand:
            cur.execute("SELECT id, brand, model FROM posts WHERE (manufacturer_id IS NULL AND brand IS NOT NULL) OR (car_model_id IS NULL AND model IS NOT NULL)")
            rows = cur.fetchall()
            for r in rows:
                p_id = r['id']
                b_str = r['brand']
                m_str = r['model']
                m_id = get_or_create_manufacturer(b_str) if b_str else None
                cm_id = get_or_create_car_model(m_id, m_str) if (m_id and m_str) else None
                
                cur.execute("UPDATE posts SET manufacturer_id = %s, car_model_id = %s WHERE id = %s", (m_id, cm_id, p_id))
            conn.commit()
            print("  -> 기존 게시글 FK 변환 완료!")
    except Exception as e:
        print(f"  -> Migration check notice: {e}")

    print("3. posts 테이블에서 레거시 컬럼 (brand, model) DROP 수행...")
    for col in ['brand', 'model']:
        try:
            cur.execute(f"ALTER TABLE posts DROP COLUMN {col}")
            print(f"  -> Successfully dropped legacy column '{col}' from posts table.")
        except Exception as e:
            print(f"  -> Column '{col}' already dropped or notice: {e}")

    conn.commit()

    print("4. 최종 posts 테이블 컬럼 구조 검증:")
    cur.execute("SHOW FULL COLUMNS FROM posts")
    cols = cur.fetchall()
    for col in cols:
        print(f"  - {col['Field']}: {col['Type']} (Null: {col['Null']})")

    cur.close()
    conn.close()
    print("posts 테이블 스키마 변경이 성공적으로 완료되었습니다!")


if __name__ == "__main__":
    alter_posts_schema()
