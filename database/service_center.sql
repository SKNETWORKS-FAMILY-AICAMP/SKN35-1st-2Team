SHOW DATABASES; -- 데이터 베이스 존재 확인

CREATE DATABASE car_recall; -- car_recall 데이터베이스가 존재하지 않는다면 실행하여 생성

USE car_recall; -- 데이터베이스 선택

SELECT DATABASE(); -- 사용중인 데이터베이스 확인

-- 서비스 센터 테이블
CREATE TABLE service_center (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '서비스센터명',
    address VARCHAR(255) NOT NULL COMMENT '주소',
    phone VARCHAR(30) COMMENT '전화번호',
    latitude DECIMAL(10,8) NOT NULL COMMENT '위도',
    longitude DECIMAL(11,8) NOT NULL COMMENT '경도',
    company VARCHAR(10) NOT NULL COMMENT '제조사',
    INDEX idx_name (name)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;

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

-- 생성된 테이블 확인
SHOW TABLES;

SELECT * FROM service_center;
SELECT * FROM legal_dong;
