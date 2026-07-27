CREATE DATABASE car_recall;

USE car_recall;

CREATE TABLE car_recall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer VARCHAR(50),       -- 제작자
    model_name VARCHAR(100),         -- 차명
    production_start DATE,          -- 생산기간(부터)
    production_end DATE,            -- 생산기간(까지)
    recall_start_date DATE,         -- 리콜개시일
    recall_count INT,               -- 리콜대수
    recall_reason TEXT              -- 리콜사유
);

SELECT database(); # database 확인

SHOW tables;		# table 확인

# 8650개 -- 사용할 데이터만 정제
SELECT manufacturer, model_name FROM car_recall WHERE manufacturer IN('벤츠', '현대자동차', '기아', '비엠더블유', '폭스바겐그룹');

# 저장 확인 용
SELECT * FROM car_recall;

# 용량 확인 용
SELECT
    table_schema AS database_name,
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'car_recall'
GROUP BY table_schema;

SELECT DATABASE();

SHOW DATABASES;

USE car_recall;

SHOW tables;

DROP DATABASE car_recall;

CREATE DATABASE car_recall;

SHOW DATABASES;











