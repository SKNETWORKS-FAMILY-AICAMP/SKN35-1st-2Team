-- 리콜 뉴스(소식) 데이터 데이터베이스 및 테이블 생성 & 초기 데이터 INSERT

USE car_recall;

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

-- 뉴스 데이터 데이터 적재 (총 14건)
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (1, '국토교통부, BYD·벤츠·현대 등 6개사 38개 차종 14만 6천대 자발적 리콜 실시', '국토교통부는 BYD코리아, 메르세데스-벤츠코리아, 스텔란티스코리아, 재규어랜드로버코리아, 현대자동차, 볼보자동차코리아에서 제작 또는 수입·판매한 총 38개 차종 146,505대에서 결함이 발견되어 자발적으로 시정조치(리콜)를 한다고 밝혔다.', 'https://www.molit.go.kr/USR/NEWS/m_71/dtl.jsp?id=95089851', '국토교통부', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (2, 'BYD Atto3 등 2개 차종, 좌석 안전띠 미착용 경고음 미표시 관련 리콜', 'BYD코리아에서 수입·판매한 Atto3 등 2개 차종에서 안전기준 부적합 사항인 좌석 안전띠 미착용 시 경고음 미표시 현상이 발견되어 제어 소프트웨어 업데이트 무상 리콜을 실시한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '자동차리콜센터', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (3, '메르세데스-벤츠 E-Class 등 14개 차종, 스티어링 휠 전자회로 내구성 부족 시정조치', '메르세데스-벤츠코리아의 E 300 등 14개 차종에서 스티어링 휠 전자장치 제어 회로보드 내구성 부족으로 핸들 가열 및 손떼기 감지 기능 오작동 가능성이 확인되어 기판 무상 교체를 개시한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '한국교통안전공단', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (4, '스텔란티스 지프 체로키·푸조 3008, 고압 연료펌프 내구성 저하 시동꺼짐 위험 조치', '스텔란티스코리아에서 수입한 지프 체로키 및 푸조 3008 디젤 차종에서 고압 연료펌프 내 마모로 인한 쇳가루 발생 시 시동 꺼짐 가능성이 제기되어 고압 펌프 부품 통째 교체를 추진한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '국토교통부', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (5, '현대자동차 싼타페·투싼 등 5개 차종, 계기판 제어 통신 소프트웨어 오류 업데이트', '현대자동차 싼타페(MX5), 투싼 등 일부 차량의 계기판 디지털 클러스터 화면 시동 초기화 시 블랙아웃 증상이 간헐적 발생하는 건과 관련해 정비 네트워크에서 소프트웨어 업데이트 패치를 제공한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '자동차리콜센터', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (6, '볼보 XC60·XC90 B5, 48V 마일드 하이브리드 발전기 부속 조림 강화 시정', '볼보자동차코리아는 XC60 및 XC90 48V 마일드 하이브리드 모델에서 스타터 발전기 고정 벨트 체결 유격으로 인한 배터리 경고등 점등 위험에 대비해 퓨즈 및 고정 벨트를 전량 점검 교체한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '한국교통안전공단', '2026-07-02');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (7, '국토교통부, 4월 대규모 리콜 발표... 현대·기아·토요타·KGM 53만대 대상', '국토교통부는 현대자동차, 기아, 한국토요타자동차, KG모빌리티 등 4개 제작사 17개 차종 총 532,144대에서 제작결함이 발견되어 시정조치(리콜)한다고 공식 발표했다.', 'https://www.molit.go.kr/USR/NEWS/m_71/lst.jsp', '국토교통부', '2026-04-18');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (8, '현대 쏘나타·기아 K5 등 10개 차종, 브레이크 유압 모듈(HECU) 내구성 개선 조치', '현대차 쏘나타 및 기아 K5 하이브리드 차량 등에서 브레이크 차체제어장치(HECU) 내부 합선 가능성이 발견되어 퓨즈 블록 무상 교환 및 제어 로직 보강을 시행한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '한국교통안전공단', '2026-04-18');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (9, 'KG모빌리티 토레스·토레스 EVX, 스마트 테일게이트 래치 부품 무상교환', 'KG모빌리티(구 쌍용자동차)의 대표 SUV 토레스 및 전기차 토레스 EVX 차종에서 전동 트렁크 테일게이트 래치 조립 오차로 인한 닫힘 미완성 현상 방지를 위해 래치 부품 교체를 진행한다.', 'https://www.car.go.kr/sd/newsDta/list.do', '자동차리콜센터', '2026-04-18');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (10, '국토교통부, 2월 현대·기아 등 3개사 51개 차종 18만대 시정조치 통보', '국토교통부는 현대자동차, 기아, 벤츠코리아에서 제작 또는 수입 판매한 51개 차종 179,880대에 대해 주행 중 시동 꺼짐 및 제어 모듈 미흡으로 자발적 리콜을 시행하도록 조치했다.', 'https://www.molit.go.kr/USR/NEWS/m_71/lst.jsp', '국토교통부', '2026-02-21');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (11, '현대 그랜저 IG·기아 K7, 람다 3.0 LPI 엔진 가스켓 유격 수리 조치', '현대 그랜저 IG 및 기아 K7 LPI 모델 중 특정 기간 생산분에 대해 엔진 오일 유압 센서 가스켓 마모에 따른 엔진오일 미세 누유 위험 개선을 위한 정밀 수리를 지원한다.', 'https://www.car.go.kr/ri/ntcn/list.do', '자동차리콜센터', '2026-02-21');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (12, '국토교통부 1월 발표, 현대·기아·벤츠·포르쉐 등 74개 차종 34만대 안전 리콜', '국토교통부는 새해 첫 달 현대자동차, 기아, 메르세데스-벤츠코리아, 포르쉐코리아 등 74개 차종 총 344,073대에서 제작결함이 확인되어 시정조치를 시작한다고 공개했다.', 'https://www.molit.go.kr/USR/NEWS/m_71/lst.jsp', '국토교통부', '2026-01-16');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (13, '현대 아이오닉5·기아 EV6, 통합 충전 제어 장치(ICCU) 소프트웨어 무상 업데이트', '전기차 라인업 아이오닉5, 아이오닉6, EV6 차량의 통합 충전 제어 장치(ICCU) 내부 과전류 보호 모듈 제어 소프트웨어 무상 업데이트 서비스 캠페인이 전국 직영 센터에서 개시된다.', 'https://www.car.go.kr/sd/newsDta/list.do', '한국교통안전공단', '2026-01-16');
INSERT INTO news (id, title, summary, url, source, published_at) VALUES (14, '포르쉐 타이칸, 전륜 유압 브레이크 호스 밀봉성 강화 개선품 전량 교체', '포르쉐코리아는 고성능 전기 스포츠카 타이칸 전 모델의 전륜 유압 브레이크 호스가 조향 누적으로 유연성이 저하될 가능성에 대해 강도를 보강한 신형 브레이크 호스로 교체하는 리콜을 결정했다.', 'https://www.car.go.kr/sd/newsDta/list.do', '자동차리콜센터', '2026-01-16');
