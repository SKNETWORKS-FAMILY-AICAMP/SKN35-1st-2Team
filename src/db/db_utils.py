"""
공용 DB 유틸 & 사이드바 컴포넌트
모든 페이지(main, community, create_page, edit_page, ...)에서
`from db_utils import ...` 형태로 가져다 씁니다.
"""

import sqlite3
from datetime import datetime
import streamlit as st

DB_PATH = "recall_community.db"
CATEGORIES = ["엔진/파워트레인", "전기/배터리", "브레이크/제동", "에어백/안전장치", "소프트웨어", "기타"]
BRANDS = ["현대", "기아", "제네시스", "쉐보레", "르노코리아", "KG모빌리티", "BMW", "벤츠", "테슬라", "기타"]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            category TEXT,
            author TEXT,
            created_at TEXT,
            updated_at TEXT,
            likes INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author TEXT,
            content TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- posts ----------
def add_post(title, content, brand, model, category, author):
    conn = get_conn()
    conn.execute(
        "INSERT INTO posts (title, content, brand, model, category, author, created_at, updated_at, likes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
        (title, content, brand, model, category, author,
         datetime.now().strftime("%Y-%m-%d %H:%M"), datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()


def update_post(post_id, title, content, brand, model, category):
    conn = get_conn()
    conn.execute(
        "UPDATE posts SET title=?, content=?, brand=?, model=?, category=?, updated_at=? WHERE id=?",
        (title, content, brand, model, category, datetime.now().strftime("%Y-%m-%d %H:%M"), post_id),
    )
    conn.commit()
    conn.close()


def delete_post(post_id):
    conn = get_conn()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()


def get_posts(brand_filter=None, category_filter=None, keyword=None, sort_by="최신순"):
    conn = get_conn()
    query = "SELECT * FROM posts WHERE 1=1"
    params = []
    if brand_filter and brand_filter != "전체":
        query += " AND brand = ?"
        params.append(brand_filter)
    if category_filter and category_filter != "전체":
        query += " AND category = ?"
        params.append(category_filter)
    if keyword:
        query += " AND (title LIKE ? OR content LIKE ? OR model LIKE ?)"
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw])

    query += " ORDER BY likes DESC, id DESC" if sort_by == "공감순" else " ORDER BY id DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_post(post_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return row


def like_post(post_id):
    conn = get_conn()
    conn.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()


# ---------- comments ----------
def add_comment(post_id, author, content):
    conn = get_conn()
    conn.execute(
        "INSERT INTO comments (post_id, author, content, created_at) VALUES (?, ?, ?, ?)",
        (post_id, author, content, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()


def get_comments(post_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY id ASC", (post_id,)
    ).fetchall()
    conn.close()
    return rows


def count_comments(post_id):
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) as c FROM comments WHERE post_id = ?", (post_id,)).fetchone()["c"]
    conn.close()
    return n
