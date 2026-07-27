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
    MySQL 제조사(manufacturer), 차량 모델(car_model), 게시글(posts), 댓글(comments), 뉴스(news) 테이블을 자동으로 생성합니다.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # 1) 제조사(manufacturer) 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS manufacturer (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(10)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 2) 차량 모델(car_model) 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS car_model (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manufacturer_id INT,
            name VARCHAR(100),
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 3) 게시글(posts) 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manufacturer_id INT,
            car_model_id INT,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(50),
            author VARCHAR(50),
            password VARCHAR(255),
            created_at VARCHAR(30),
            updated_at VARCHAR(30),
            likes INT DEFAULT 0,
            views INT DEFAULT 0,
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE,
            FOREIGN KEY (car_model_id) REFERENCES car_model(id) ON DELETE CASCADE,
            INDEX idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # 마이그레이션 안전장치 (기존 posts 테이블에 컬럼이 없는 경우 추가)
    try:
        cur.execute("ALTER TABLE posts ADD COLUMN manufacturer_id INT")
    except Exception:
        pass

    try:
        cur.execute("ALTER TABLE posts ADD COLUMN car_model_id INT")
    except Exception:
        pass

    try:
        cur.execute("ALTER TABLE posts ADD COLUMN views INT DEFAULT 0")
    except Exception:
        pass

    # 4) 댓글(comments) 테이블 생성 (posts 삭제 시 연쇄 삭제 FOREIGN KEY ON DELETE CASCADE 지정)
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
        pass

    try:
        cur.execute("ALTER TABLE comments ADD COLUMN updated_at VARCHAR(30) DEFAULT NULL")
    except Exception:
        pass

    # 5) 리콜 뉴스(news) 테이블 생성
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

    # 초기 제조사 및 차량 모델 시딩 (테이블이 비어있을 때만)
    _seed_initial_manufacturers_and_models(cur, conn)

    # 기존 posts 데이터 마이그레이션 (brand -> manufacturer_id, model -> car_model_id)
    _migrate_existing_posts(cur, conn)

    cur.close()
    conn.close()


def _seed_initial_manufacturers_and_models(cur, conn):
    """제조사 및 기본 차량 모델 데이터 초기 시딩 유틸"""
    cur.execute("SELECT COUNT(*) FROM manufacturer")
    row = cur.fetchone()
    count = row[0] if row else 0
    if count == 0:
        initial_data = {
            "현대": ["그랜저", "싼타페", "아반떼", "투싼", "팰리세이드", "아이오닉5", "포터2", "기타"],
            "기아": ["K5", "쏘렌토", "카니발", "스포티지", "레이", "EV6", "기타"],
            "벤츠": ["E-Class", "S-Class", "C-Class", "GLC", "GLE", "기타"],
            "BMW": ["5시리즈", "3시리즈", "X5", "X3", "7시리즈", "기타"],
            "폭스바겐": ["골프", "티구안", "파사트", "ID.4", "기타"],
        }
        for m_name, models in initial_data.items():
            cur.execute("INSERT INTO manufacturer (name) VALUES (%s)", (m_name,))
            m_id = cur.lastrowid
            for model_name in models:
                cur.execute("INSERT INTO car_model (manufacturer_id, name) VALUES (%s, %s)", (m_id, model_name))
        conn.commit()


def _migrate_existing_posts(cur, conn):
    """기존 posts 테이블의 brand 및 model 문자열 데이터를 manufacturer_id 및 car_model_id로 마이그레이션"""
    try:
        cur.execute("SELECT id, brand, model FROM posts WHERE (manufacturer_id IS NULL AND brand IS NOT NULL AND brand != '') OR (car_model_id IS NULL AND model IS NOT NULL AND model != '')")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                p_id = r[0] if isinstance(r, tuple) else r.get('id')
                b_str = r[1] if isinstance(r, tuple) else r.get('brand')
                m_str = r[2] if isinstance(r, tuple) else r.get('model')
                
                m_id = get_or_create_manufacturer(b_str) if b_str else None
                cm_id = get_or_create_car_model(m_id, m_str) if (m_id and m_str) else None
                
                cur.execute("UPDATE posts SET manufacturer_id = %s, car_model_id = %s WHERE id = %s", (m_id, cm_id, p_id))
            conn.commit()
    except Exception:
        pass


# ==========================================
# 제조사 (manufacturer) 및 차량 모델 (car_model) 유틸
# ==========================================

def get_manufacturers():
    """전체 제조사 목록 조회 (dict 리스트 반환)"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name FROM manufacturer ORDER BY name ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_car_models(manufacturer_id=None):
    """특정 제조사(또는 전체)의 차량 모델 목록 조회 (dict 리스트 반환)"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    if manufacturer_id:
        cur.execute("SELECT id, manufacturer_id, name FROM car_model WHERE manufacturer_id = %s ORDER BY name ASC", (manufacturer_id,))
    else:
        cur.execute("SELECT id, manufacturer_id, name FROM car_model ORDER BY name ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_or_create_manufacturer(name):
    """제조사 명칭으로 ID 조회 (없을 경우 자동 생성 후 ID 반환)"""
    if not name or not str(name).strip():
        return None
    name_clean = str(name).strip()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM manufacturer WHERE name = %s", (name_clean,))
    row = cur.fetchone()
    if row:
        m_id = row['id']
    else:
        cur.execute("INSERT INTO manufacturer (name) VALUES (%s)", (name_clean,))
        conn.commit()
        m_id = cur.lastrowid
    cur.close()
    conn.close()
    return m_id


def get_or_create_car_model(manufacturer_id, name):
    """제조사 ID 및 차량 모델 명칭으로 ID 조회 (없을 경우 자동 생성 후 ID 반환)"""
    if not name or not str(name).strip() or not manufacturer_id:
        return None
    name_clean = str(name).strip()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM car_model WHERE manufacturer_id = %s AND name = %s", (manufacturer_id, name_clean))
    row = cur.fetchone()
    if row:
        cm_id = row['id']
    else:
        cur.execute("INSERT INTO car_model (manufacturer_id, name) VALUES (%s, %s)", (manufacturer_id, name_clean))
        conn.commit()
        cm_id = cur.lastrowid
    cur.close()
    conn.close()
    return cm_id


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

def add_post(title, content, brand=None, model=None, category="기타", author="익명", password="1234", manufacturer_id=None, car_model_id=None):
    """새로운 커뮤니티 게시글을 DB에 작성 (manufacturer_id, car_model_id FK 지원)"""
    if not manufacturer_id and brand:
        manufacturer_id = get_or_create_manufacturer(brand)
    if not car_model_id and model and manufacturer_id:
        car_model_id = get_or_create_car_model(manufacturer_id, model)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO posts (title, content, manufacturer_id, car_model_id, category, author, password, created_at, updated_at, likes, views)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0)
        """,
        (title, content, manufacturer_id, car_model_id, category, author, password,
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


def update_post(post_id, title, content, brand=None, model=None, category="기타", manufacturer_id=None, car_model_id=None):
    """기존 게시글의 정보(제목, 내용, 제조사 ID, 모델 ID, 카테고리) 및 수정일시(updated_at) 갱신"""
    if not manufacturer_id and brand:
        manufacturer_id = get_or_create_manufacturer(brand)
    if not car_model_id and model and manufacturer_id:
        car_model_id = get_or_create_car_model(manufacturer_id, model)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE posts SET title=%s, content=%s, manufacturer_id=%s, car_model_id=%s, category=%s, updated_at=%s WHERE id=%s
        """,
        (title, content, manufacturer_id, car_model_id, category, datetime.now().strftime("%Y-%m-%d %H:%M"), post_id),
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
    manufacturer 및 car_model 테이블과 LEFT JOIN하여 게시글 목록 조회 (brand, model 명칭 자동 로드)
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.id,
            p.manufacturer_id,
            p.car_model_id,
            p.title,
            p.content,
            p.category,
            p.author,
            p.password,
            p.created_at,
            p.updated_at,
            COALESCE(p.likes, 0) AS likes,
            COALESCE(p.views, 0) AS views,
            COALESCE(m.name, p.brand, '') AS brand,
            COALESCE(cm.name, p.model, '') AS model
        FROM posts p
        LEFT JOIN manufacturer m ON p.manufacturer_id = m.id
        LEFT JOIN car_model cm ON p.car_model_id = cm.id
        WHERE 1=1
    """
    params = []
    
    # 브랜드/제조사 필터 조건
    if brand_filter and brand_filter != "전체":
        if str(brand_filter).isdigit():
            query += " AND p.manufacturer_id = %s"
            params.append(int(brand_filter))
        else:
            query += " AND m.name = %s"
            params.append(brand_filter)
        
    # 카테고리 필터 조건
    if category_filter and category_filter != "전체":
        query += " AND p.category = %s"
        params.append(category_filter)
        
    # 키워드 검색 범위 조건 동적 생성
    if keyword and str(keyword).strip():
        kw = f"%{str(keyword).strip()}%"
        if search_target == "제목만":
            query += " AND p.title LIKE %s"
            params.append(kw)
        elif search_target == "내용만":
            query += " AND p.content LIKE %s"
            params.append(kw)
        elif search_target == "제목+내용":
            query += " AND (p.title LIKE %s OR p.content LIKE %s)"
            params.extend([kw, kw])
        else:  # "전체" (제목 + 내용 + 모델 + 작성자 통합 검색)
            query += " AND (p.title LIKE %s OR p.content LIKE %s OR cm.name LIKE %s OR p.author LIKE %s)"
            params.extend([kw, kw, kw, kw])

    # 정렬 방식 지정 (조회순, 공감순, 최신순)
    if sort_by == "조회순":
        query += " ORDER BY p.views DESC, p.created_at DESC, p.id DESC"
    elif sort_by == "공감순":
        query += " ORDER BY p.likes DESC, p.created_at DESC, p.id DESC"
    else:  # 최신순
        query += " ORDER BY p.created_at DESC, p.id DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_post(post_id):
    """단일 게시글 상세 데이터 조회 (manufacturer 및 car_model LEFT JOIN)"""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.id,
            p.manufacturer_id,
            p.car_model_id,
            p.title,
            p.content,
            p.category,
            p.author,
            p.password,
            p.created_at,
            p.updated_at,
            COALESCE(p.likes, 0) AS likes,
            COALESCE(p.views, 0) AS views,
            COALESCE(m.name, p.brand, '') AS brand,
            COALESCE(cm.name, p.model, '') AS model
        FROM posts p
        LEFT JOIN manufacturer m ON p.manufacturer_id = m.id
        LEFT JOIN car_model cm ON p.car_model_id = cm.id
        WHERE p.id = %s
    """
    cur.execute(query, (post_id,))
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

