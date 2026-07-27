-- 커뮤니티(소통공간) 테이블 생성 DDL

USE car_recall;

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT '게시글 제목',
    content TEXT NOT NULL COMMENT '게시글 본문',
    brand VARCHAR(50) COMMENT '차량 브랜드',
    model VARCHAR(100) COMMENT '차량 모델명',
    category VARCHAR(50) COMMENT '카테고리',
    author VARCHAR(50) COMMENT '작성자 닉네임',
    password VARCHAR(255) COMMENT '수정/삭제용 비밀번호',
    created_at VARCHAR(30) COMMENT '작성일시',
    updated_at VARCHAR(30) COMMENT '수정일시',
    likes INT DEFAULT 0 COMMENT '공감(좋아요) 수',
	views INT DEFAULT 0,
    INDEX idx_brand (brand),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL COMMENT '게시글 ID',
    author VARCHAR(50) COMMENT '작성자 닉네임',
    content TEXT NOT NULL COMMENT '댓글 본문',
    created_at VARCHAR(30) COMMENT '작성일시',
	password
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    INDEX idx_post_id (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
