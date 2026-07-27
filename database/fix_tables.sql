show databases; -- 현재 존재하는 데이버테이스 목록 확인

USE car_recall; -- 데이터베이스 선택 car_recall이 없다면 create database car_recall; 실행
SELECT DATABASE(); -- 선택한 데이터베이스 확인

-- 제조사
CREATE TABLE manufacturer(
	id int auto_increment primary key,
    name varchar(10)
);

-- 차량 모델
CREATE TABLE car_model(
	id int auto_increment primary key,
    manufacturer_id int,
    name varchar(100),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE
);

SHOW TABLE car_model;

-- car_recall
CREATE TABLE car_recall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_model_id int,            	-- 제조사 id
    production_start DATE,          -- 생산기간(부터)
    production_end DATE,            -- 생산기간(까지)
    recall_start_date DATE,         -- 리콜개시일
    recall_count INT,               -- 리콜대수
    recall_reason TEXT,				-- 리콜사유
    FOREIGN KEY (car_model_id) REFERENCES car_model(id) ON DELETE CASCADE
);


-- 서비스 센터 테이블
CREATE TABLE service_center (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT, 
    name VARCHAR(100) NOT NULL COMMENT '서비스센터명',
    address VARCHAR(255) NOT NULL COMMENT '주소',
    phone VARCHAR(30) COMMENT '전화번호',
    latitude DECIMAL(10,8) NOT NULL COMMENT '위도',
    longitude DECIMAL(11,8) NOT NULL COMMENT '경도',
    
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id) ON DELETE CASCADE,
    INDEX idx_name (name)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;

-- posts
CREATE TABLE IF NOT EXISTS posts (
	id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT,
    car_model_id int,
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



-- comments
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



-- NEWS
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '뉴스 고유 ID',
    title VARCHAR(255) NOT NULL COMMENT '뉴스 제목',
    summary TEXT NOT NULL COMMENT '뉴스 요약 내용',
    url VARCHAR(500) NOT NULL COMMENT '원문 보도자료 URL',
    source VARCHAR(100) DEFAULT '국토교통부' COMMENT '언론사 및 출처',
    published_at VARCHAR(30) NOT NULL COMMENT '보도 일자 (YYYY-MM-DD)',
    INDEX idx_published_at (published_at),
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 법정동 테이블
CREATE TABLE legal_dong (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sido_name VARCHAR(30) NOT NULL COMMENT '시도명',
    sigungu_name VARCHAR(30) NULL COMMENT '시군구명',
    eupmyeondong_name VARCHAR(50) NULL COMMENT '읍면동명',
    ri_name VARCHAR(50) NULL COMMENT '리명',

    INDEX idx_sido (sido_name),
    INDEX idx_sigungu (sigungu_name),
    INDEX idx_eupmyeondong (eupmyeondong_name)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;


-- FAQ
CREATE  TABLE faq (
    page INT AUTO_INCREMENT PRIMARY KEY,
    category TEXT,
    source TEXT,
    question TEXT,
    answer TEXT,
    source_url TEXT
);