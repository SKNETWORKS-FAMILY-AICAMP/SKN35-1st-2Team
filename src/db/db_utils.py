# 수정일자: 2026-07-26
"""
공용 DB 유틸 (MySQL 기반)
모든 페이지(main, community, create_page, edit_page, ...)에서 사용됩니다.
"""

import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 설정 및 .env 로드
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CATEGORIES = ["엔진/파워트레인", "전기/배터리", "브레이크/제동", "에어백/안전장치", "소프트웨어", "기타"]
BRANDS = ["현대", "기아", "제네시스", "쉐보레", "르노코리아", "KG모빌리티", "BMW", "벤츠", "테슬라", "기타"]


def get_conn():
    """MySQL 연결 객체 반환"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_DATABASE", "car_recall"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


def init_db():
    """MySQL 커뮤니티 테이블(posts, comments)이 없을 경우 생성하고, views 컬럼이 없으면 추가합니다."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            brand VARCHAR(50),
            model VARCHAR(100),
            category VARCHAR(50),
            author VARCHAR(50),
            password VARCHAR(255),
            created_at VARCHAR(30),
            updated_at VARCHAR(30),
            likes INT DEFAULT 0,
            views INT DEFAULT 0,
            INDEX idx_brand (brand),
            INDEX idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    # views 컬럼 유무 확인 및 자동 추가 (기존 테이블 마이그레이션 안전장치)
    try:
        cur.execute("ALTER TABLE posts ADD COLUMN views INT DEFAULT 0")
    except Exception:
        pass  # 이미 컬럼이 존재하는 경우 예외 무시

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            author VARCHAR(50),
            content TEXT NOT NULL,
            password VARCHAR(255) DEFAULT '1234',
            created_at VARCHAR(30),
            updated_at VARCHAR(30) DEFAULT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            INDEX idx_post_id (post_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    try:
        cur.execute("ALTER TABLE comments ADD COLUMN password VARCHAR(255) DEFAULT '1234'")
    except Exception:
        pass  # 이미 컬럼이 있는 경우 무시

    try:
        cur.execute("ALTER TABLE comments ADD COLUMN updated_at VARCHAR(30) DEFAULT NULL")
    except Exception:
        pass  # 이미 컬럼이 있는 경우 무시
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            summary TEXT NOT NULL,
            url VARCHAR(500) NOT NULL,
            source VARCHAR(100) DEFAULT '국토교통부',
            published_at VARCHAR(30) NOT NULL,
            INDEX idx_published_at (published_at),
            INDEX idx_title (title)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    conn.commit()
    cur.close()
    conn.close()


def increment_views(post_id):
    """게시글 조회수 1 증가"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET views = COALESCE(views, 0) + 1 WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------- posts ----------
def add_post(title, content, brand, model, category, author, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO posts (title, content, brand, model, category, author, password, created_at, updated_at, likes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
        """,
        (title, content, brand, model, category, author, password,
         datetime.now().strftime("%Y-%m-%d %H:%M"), datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    cur.close()
    conn.close()


def verify_post_password(post_id, input_password):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT password FROM posts WHERE id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return False
    stored_password = row["password"] or ""
    return stored_password == (input_password or "")


def update_post(post_id, title, content, brand, model, category):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE posts SET title=%s, content=%s, brand=%s, model=%s, category=%s, updated_at=%s WHERE id=%s
        """,
        (title, content, brand, model, category, datetime.now().strftime("%Y-%m-%d %H:%M"), post_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_post(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_posts(brand_filter=None, category_filter=None, keyword=None, sort_by="최신순", search_target="제목+내용"):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = "SELECT * FROM posts WHERE 1=1"
    params = []
    if brand_filter and brand_filter != "전체":
        query += " AND brand = %s"
        params.append(brand_filter)
    if category_filter and category_filter != "전체":
        query += " AND category = %s"
        params.append(category_filter)
    if keyword and str(keyword).strip():
        kw = f"%{str(keyword).strip()}%"
        if search_target == "제목만":
            query += " AND title LIKE %s"
            params.append(kw)
        elif search_target == "내용만":
            query += " AND content LIKE %s"
            params.append(kw)
        elif search_target == "제목+내용":
            query += " AND (title LIKE %s OR content LIKE %s)"
            params.extend([kw, kw])
        else:  # "전체" (제목+내용+모델+작성자)
            query += " AND (title LIKE %s OR content LIKE %s OR model LIKE %s OR author LIKE %s)"
            params.extend([kw, kw, kw, kw])

    if sort_by == "조회순":
        query += " ORDER BY views DESC, created_at DESC, id DESC"
    elif sort_by == "공감순":
        query += " ORDER BY likes DESC, created_at DESC, id DESC"
    else:
        # 최신순 정렬: 작성일시(created_at) 내림차순 기준
        query += " ORDER BY created_at DESC, id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_post(post_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def like_post(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = likes + 1 WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


def unlike_post(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = GREATEST(0, likes - 1) WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------- comments ----------
def add_comment(post_id, author, content, password="1234"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO comments (post_id, author, content, password, created_at) VALUES (%s, %s, %s, %s, %s)
        """,
        (post_id, author, content, password or "1234", datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    cur.close()
    conn.close()


def verify_comment_password(comment_id, input_password):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT password FROM comments WHERE id = %s", (comment_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return False
    stored = row["password"] or "1234"
    return stored == (input_password or "1234")


def update_comment(comment_id, content):
    conn = get_conn()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute("UPDATE comments SET content = %s, updated_at = %s WHERE id = %s", (content, now_str, comment_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_comment(comment_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_comments(post_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM comments WHERE post_id = %s ORDER BY id ASC", (post_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def count_comments(post_id):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) as c FROM comments WHERE post_id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["c"] if row else 0


# ---------- news ----------
def add_news(title, summary, url, source="국토교통부", published_at=None):
    if not published_at:
        published_at = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO news (title, summary, url, source, published_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (title, summary, url, source, published_at),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_news_sources():
    """DB에 등록된 고유 출처/언론사 목록 반환"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT source FROM news WHERE source IS NOT NULL AND source != '' ORDER BY source ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["source"] for r in rows]


def get_news(keyword=None, source_filter=None, sort_by="최신순"):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = "SELECT * FROM news WHERE 1=1"
    params = []
    if source_filter and source_filter != "전체":
        query += " AND source = %s"
        params.append(source_filter)
    if keyword and str(keyword).strip():
        kw = f"%{str(keyword).strip()}%"
        query += " AND title LIKE %s"
        params.append(kw)

    if sort_by == "오래된순":
        query += " ORDER BY published_at ASC, id ASC"
    else:  # 최신순
        query += " ORDER BY published_at DESC, id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def count_news(keyword=None, source_filter=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = "SELECT COUNT(*) as c FROM news WHERE 1=1"
    params = []
    if source_filter and source_filter != "전체":
        query += " AND source = %s"
        params.append(source_filter)
    if keyword and str(keyword).strip():
        kw = f"%{str(keyword).strip()}%"
        query += " AND title LIKE %s"
        params.append(kw)

    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["c"] if row else 0
