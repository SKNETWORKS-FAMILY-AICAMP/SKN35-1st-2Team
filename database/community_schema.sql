-- 커뮤니티(소통공간) 테이블 생성 DDL

CREATE DATABASE IF NOT EXISTS car_recall;
USE car_recall;

-- 1. 제조사 테이블
CREATE TABLE IF NOT EXISTS manufacturer (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '제조사 고유 ID',
    name VARCHAR(10) COMMENT '제조사 명칭 (예: 현대, 기아, 벤츠 등)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 차량 모델 테이블
CREATE TABLE IF NOT EXISTS car_model (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '차량 모델 고유 ID',
    manufacturer_id INT COMMENT '제조사 ID (FK)',
    name VARCHAR(100) COMMENT '모델 명칭 (예: 그랜저, K5 등)',
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 게시글 테이블
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '게시글 ID',
    manufacturer_id INT COMMENT '제조사 ID (FK)',
    car_model_id INT COMMENT '차량 모델 ID (FK)',
    title VARCHAR(255) NOT NULL COMMENT '게시글 제목',
    content TEXT NOT NULL COMMENT '게시글 본문',
    category VARCHAR(50) COMMENT '카테고리',
    author VARCHAR(50) COMMENT '작성자 닉네임',
    password VARCHAR(255) COMMENT '수정/삭제용 비밀번호',
    created_at VARCHAR(30) COMMENT '작성일시',
    updated_at VARCHAR(30) COMMENT '수정일시',
    likes INT DEFAULT 0 COMMENT '공감(좋아요) 수',
    views INT DEFAULT 0 COMMENT '조회수',

    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE,
    FOREIGN KEY (car_model_id) REFERENCES car_model(id) ON DELETE CASCADE,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 댓글 테이블
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '댓글 ID',
    post_id INT NOT NULL COMMENT '게시글 ID (FK)',
    author VARCHAR(50) COMMENT '작성자 닉네임',
    content TEXT NOT NULL COMMENT '댓글 본문',
    password VARCHAR(255) DEFAULT '1234' COMMENT '수정/삭제용 비밀번호',
    created_at VARCHAR(30) COMMENT '작성일시',
    updated_at VARCHAR(30) DEFAULT NULL COMMENT '수정일시',
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    INDEX idx_post_id (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
