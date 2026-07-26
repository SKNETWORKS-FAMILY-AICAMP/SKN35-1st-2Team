import os
import sys

# src 디렉토리를 sys.path 최상단에 추가
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from db.database import get_db_connection

def dump_news_sql():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM news ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    sql_lines = []
    sql_lines.append("-- 리콜 뉴스(소식) 데이터 데이터베이스 및 테이블 생성 & 초기 데이터 INSERT")
    sql_lines.append("")
    sql_lines.append("USE car_recall;")
    sql_lines.append("")
    sql_lines.append("CREATE TABLE IF NOT EXISTS news (")
    sql_lines.append("    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '뉴스 고유 ID',")
    sql_lines.append("    title VARCHAR(255) NOT NULL COMMENT '뉴스 제목',")
    sql_lines.append("    summary TEXT NOT NULL COMMENT '뉴스 요약 내용',")
    sql_lines.append("    url VARCHAR(500) NOT NULL COMMENT '원문 보도자료 URL',")
    sql_lines.append("    source VARCHAR(100) DEFAULT '국토교통부' COMMENT '언론사 및 출처',")
    sql_lines.append("    published_at VARCHAR(30) NOT NULL COMMENT '보도 일자 (YYYY-MM-DD)',")
    sql_lines.append("    INDEX idx_published_at (published_at),")
    sql_lines.append("    INDEX idx_title (title)")
    sql_lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
    sql_lines.append("")
    sql_lines.append("-- 뉴스 데이터 데이터 적재 (총 14건)")

    for r in rows:
        title = r['title'].replace("'", "''")
        summary = r['summary'].replace("'", "''")
        url = r['url'].replace("'", "''")
        source = r['source'].replace("'", "''") if r['source'] else '국토교통부'
        published_at = r['published_at'].replace("'", "''")
        
        line = f"INSERT INTO news (id, title, summary, url, source, published_at) VALUES ({r['id']}, '{title}', '{summary}', '{url}', '{source}', '{published_at}');"
        sql_lines.append(line)

    sql_content = "\n".join(sql_lines) + "\n"
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "news.sql"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print(f"Successfully generated {output_path} with {len(rows)} news items.")

if __name__ == "__main__":
    dump_news_sql()
