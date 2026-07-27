"""
공용 DB 유틸 (MySQL 기반)
모든 페이지(main, community, create_page, edit_page, news 등)에서 사용됩니다.
"""

import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

# 1. 프로젝트 루트 디렉토리 설정 및 .env 환경 변수 로드
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 2. 커뮤니티 전역 사용 카테고리 및 차종 브랜드 목록 상수
CATEGORIES = ["엔진/파워트레인", "전기/배터리", "브레이크/제동", "에어백/안전장치", "소프트웨어", "기타"]
BRANDS = ["현대", "기아", "벤츠", "BMW", "폭스바겐"]


def get_conn():
    """MySQL 연결 커넥션 객체 생성 및 반환 (.env 설정 활용)"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_DATABASE", "car_recall"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


def init_db():
    """
    MySQL 커뮤니티 테이블(posts, comments) 및 뉴스 테이블(news)을 자동으로 생성하고,
    기존 데이터베이스 마이그레이션을 위한 컬럼 안전장치(ALTER TABLE)를 수행합니다.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # 1) 게시글(posts) 테이블 생성
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
    
    # views 컬럼 유무 확인 및 자동 추가 (기존 테이블 호환성 마이그레이션 안전장치)
    try:
        cur.execute("ALTER TABLE posts ADD COLUMN views INT DEFAULT 0")
    except Exception:
        pass  # 이미 컬럼이 존재하는 경우 예외 무시

    # 2) 댓글(comments) 테이블 생성 (posts 삭제 시 연쇄 삭제 FOREIGN KEY ON DELETE CASCADE 지정)
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
    
    # 댓글 마이그레이션 안전장치: 비밀번호 및 수정일시 컬럼 추가
    try:
        cur.execute("ALTER TABLE comments ADD COLUMN password VARCHAR(255) DEFAULT '1234'")
    except Exception:
        pass

    try:
        cur.execute("ALTER TABLE comments ADD COLUMN updated_at VARCHAR(30) DEFAULT NULL")
    except Exception:
        pass

    # 3) 리콜 뉴스(news) 테이블 생성
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
    """게시글 조회수 1 증가 (COALESCE 처리로 NULL 방지)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET views = COALESCE(views, 0) + 1 WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# 게시글 (posts) CRUD 및 비즈니스 로직
# ==========================================

def add_post(title, content, brand, model, category, author, password):
    """새로운 커뮤니티 게시글을 DB에 작성"""
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
    """게시글 수정/삭제 전 입력된 비밀번호가 DB 값과 일치하는지 검증 (Boolean 반환)"""
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
    """기존 게시글의 정보(제목, 내용, 브랜드, 모델, 카테고리) 및 수정일시(updated_at) 갱신"""
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
    """특정 게시글 및 하위 댓글 일괄 삭제"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_posts(brand_filter=None, category_filter=None, keyword=None, sort_by="최신순", search_target="제목+내용"):
    """
    브랜드, 카테고리, 키워드, 검색 범위(제목/내용/전체) 및 정렬 조건(최신순/조회순/공감순)에 맞춰 게시글 목록 조회
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = "SELECT * FROM posts WHERE 1=1"
    params = []
    
    # 브랜드 필터 조건
    if brand_filter and brand_filter != "전체":
        query += " AND brand = %s"
        params.append(brand_filter)
        
    # 카테고리 필터 조건
    if category_filter and category_filter != "전체":
        query += " AND category = %s"
        params.append(category_filter)
        
    # 키워드 검색 범위 조건 동적 생성
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
        else:  # "전체" (제목 + 내용 + 모델 + 작성자 통합 검색)
            query += " AND (title LIKE %s OR content LIKE %s OR model LIKE %s OR author LIKE %s)"
            params.extend([kw, kw, kw, kw])

    # 정렬 방식 지정 (조회순, 공감순, 최신순)
    if sort_by == "조회순":
        query += " ORDER BY views DESC, created_at DESC, id DESC"
    elif sort_by == "공감순":
        query += " ORDER BY likes DESC, created_at DESC, id DESC"
    else:  # 최신순
        query += " ORDER BY created_at DESC, id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_post(post_id):
    """단일 게시글 상세 데이터 조회"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def like_post(post_id):
    """게시글 공감(좋아요) 수 1 증가"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = likes + 1 WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


def unlike_post(post_id):
    """게시글 공감(좋아요) 취소 - 최소값 0 유지 (GREATEST 처리)"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE posts SET likes = GREATEST(0, likes - 1) WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# 댓글 (comments) CRUD 및 비즈니스 로직
# ==========================================

def add_comment(post_id, author, content, password="1234"):
    """게시글 하위에 새로운 댓글 작성"""
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
    """댓글 수정/삭제 전 입력된 비밀번호 검증 (Boolean 반환)"""
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
    """기존 댓글 내용 수정 및 수정일시(updated_at) 기록"""
    conn = get_conn()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute("UPDATE comments SET content = %s, updated_at = %s WHERE id = %s", (content, now_str, comment_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_comment(comment_id):
    """특정 댓글 삭제"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_comments(post_id):
    """특정 게시글에 작성된 전체 댓글 목록 조회 (오래된 순 정렬)"""
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
    """특정 게시글의 총 댓글 수 반환"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) as c FROM comments WHERE post_id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["c"] if row else 0


# ==========================================
# 소식/뉴스 (news) CRUD 및 비즈니스 로직
# ==========================================

def add_news(title, summary, url, source="국토교통부", published_at=None):
    """새로운 리콜 뉴스 데이터를 DB에 추가"""
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
    """DB에 저장되어 있는 언론사/출처 고유 목록(DISTINCT) 조회"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT source FROM news WHERE source IS NOT NULL AND source != '' ORDER BY source ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["source"] for r in rows]


def get_news(keyword=None, source_filter=None, sort_by="최신순"):
    """키워드 검색, 언론사/출처 필터, 정렬 조건(최신순/오래된순)에 맞춰 뉴스 목록 조회"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = "SELECT * FROM news WHERE 1=1"
    params = []
    
    # 출처 필터링
    if source_filter and source_filter != "전체":
        query += " AND source = %s"
        params.append(source_filter)
        
    # 뉴스 제목 키워드 검색
    if keyword and str(keyword).strip():
        kw = f"%{str(keyword).strip()}%"
        query += " AND title LIKE %s"
        params.append(kw)

    # 정렬 방식 지정 (최신순 / 오래된순)
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
    """조건에 맞는 리콜 뉴스의 전체 개수 카운트"""
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

