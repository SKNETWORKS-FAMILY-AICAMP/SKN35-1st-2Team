"""
자동차리콜센터 리콜보도자료 크롤링
대상: https://www.car.go.kr/sd/newsDta/list.do

주요 개선사항
1. 페이지마다 CSV 중간 저장
2. 중간에 멈춰도 마지막 저장 페이지 다음부터 재시작
3. 연결 오류 발생 시 재시도
4. WebDriver 오류 시 브라우저를 다시 실행
5. Streamlit과 별도 터미널에서 실행
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# =========================================================
# 1. 기본 설정
# =========================================================
BASE_URL = "https://www.car.go.kr/sd/newsDta/list.do"

# 실제 사이트 기준 전체 페이지 수는 달라질 수 있습니다.
# 처음 테스트할 때는 3으로 설정하고, 정상 동작 확인 후 121 등으로 변경하세요.
MAX_PAGES = 121

# 페이지 하나를 수집한 뒤 기다리는 시간
PAGE_DELAY = 1.5

# 한 페이지에서 오류가 날 때 재시도 횟수
MAX_RETRIES = 3

# 브라우저를 화면에 보이지 않게 실행하려면 True
# 문제 확인 중에는 False를 추천합니다.
HEADLESS = False

# 현재 파일 위치를 기준으로 프로젝트 루트와 저장 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "crawled"
OUTPUT_FILE = OUTPUT_DIR / "recall_news.csv"

# CSV 컬럼 순서
CSV_COLUMNS = ["페이지", "제목", "내용", "작성자", "등록일", "조회수"]


# =========================================================
# 2. ChromeDriver 실행
# =========================================================
def create_driver() -> webdriver.Chrome:
    """Selenium Chrome 브라우저를 생성합니다."""

    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1600,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")

    # 자동화 탐지 관련 옵션을 최소화합니다.
    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation", "enable-logging"],
    )
    options.add_experimental_option(
        "useAutomationExtension",
        False,
    )

    # Selenium 4.6 이상은 ChromeDriver를 자동으로 관리합니다.
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(40)

    return driver


# =========================================================
# 3. 문자열 정리
# =========================================================
def clean_text(value: Any) -> str:
    """연속 공백과 줄바꿈을 한 칸으로 정리합니다."""

    if value is None:
        return ""

    text = str(value)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_date(text: str) -> str:
    """문자열에서 YYYY-MM-DD 형식 날짜를 찾습니다."""

    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return match.group(0) if match else ""


def extract_views(text: str) -> str:
    """문자열에서 조회수 숫자를 찾습니다."""

    match = re.search(r"조회수\s*[:：]?\s*([\d,]+)", text)

    if not match:
        return ""

    return match.group(1).replace(",", "")


def split_title_content(text: str) -> tuple[str, str]:
    """
    링크 안의 텍스트를 제목과 내용으로 분리합니다.

    자동차리콜센터 목록은 보통
    '제목 □ 내용' 형태로 표시되므로 첫 번째 구분기호를 기준으로 나눕니다.
    """

    cleaned = clean_text(text)

    # 사이트에서 사용될 수 있는 네모/불릿 계열 구분기호를 함께 처리
    match = re.search(r"\s*[□■▪●◇◆]\s*", cleaned)

    if not match:
        return cleaned, ""

    title = clean_text(cleaned[:match.start()])
    content = clean_text(cleaned[match.end():])

    return title, content


# =========================================================
# 4. 현재 페이지 번호 확인
# =========================================================
def get_current_page(driver: webdriver.Chrome) -> int | None:
    """화면에서 현재 활성화된 페이지 번호를 찾습니다."""

    selectors = [
        ".pagination .active",
        ".paging .active",
        ".page_num .on",
        ".pagination .on",
        ".paging .on",
        "strong",
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)

            for element in elements:
                text = clean_text(element.text)

                if text.isdigit():
                    return int(text)

        except WebDriverException:
            continue

    # 페이지 상단의 '페이지 1/121' 형식에서 찾기
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        match = re.search(r"페이지\s*(\d+)\s*/\s*\d+", body_text)

        if match:
            return int(match.group(1))

    except WebDriverException:
        pass

    return None


# =========================================================
# 5. 페이지 목록 파싱
# =========================================================
def find_news_blocks(soup: BeautifulSoup) -> list[Any]:
    """
    뉴스 게시물 블록을 찾습니다.

    사이트 HTML 구조가 조금 바뀌어도 동작하도록
    여러 후보 선택자와 일반 탐색 방식을 함께 사용합니다.
    """

    candidate_selectors = [
        ".board_list > li",
        ".board-list > li",
        ".news_list > li",
        ".news-list > li",
        ".list_wrap > ul > li",
        ".list-wrap > ul > li",
        ".bbs_list > li",
        ".bbs-list > li",
        "ul.list > li",
    ]

    for selector in candidate_selectors:
        blocks = soup.select(selector)
        valid_blocks = [
            block
            for block in blocks
            if "조회수" in clean_text(block.get_text(" ", strip=True))
            and extract_date(clean_text(block.get_text(" ", strip=True)))
        ]

        if valid_blocks:
            return valid_blocks

    # 선택자를 못 찾았을 때:
    # 날짜와 조회수가 함께 있는 가장 안쪽 li 태그를 찾습니다.
    valid_blocks = []

    for block in soup.find_all("li"):
        text = clean_text(block.get_text(" ", strip=True))

        if "조회수" not in text:
            continue

        if not extract_date(text):
            continue

        # 자식 li에도 같은 게시물 정보가 있으면 바깥쪽 li는 제외합니다.
        nested_valid = False

        for child in block.find_all("li", recursive=False):
            child_text = clean_text(child.get_text(" ", strip=True))

            if "조회수" in child_text and extract_date(child_text):
                nested_valid = True
                break

        if not nested_valid:
            valid_blocks.append(block)

    return valid_blocks


def parse_news_block(block: Any, page_number: int) -> dict[str, str]:
    """게시물 한 개에서 제목, 내용, 작성자, 날짜, 조회수를 추출합니다."""

    full_text = clean_text(block.get_text(" ", strip=True))

    # 링크 텍스트에서 '제목 □ 내용'을 먼저 분리합니다.
    links = block.find_all("a")
    link_texts = [
        clean_text(link.get_text(" ", strip=True))
        for link in links
        if clean_text(link.get_text(" ", strip=True))
    ]

    title = ""
    content = ""

    if link_texts:
        main_link_text = max(link_texts, key=len)
        title, content = split_title_content(main_link_text)

    # 링크에서 제목을 찾지 못했을 때 제목 후보 태그 사용
    if not title:
        for selector in [
            ".title",
            ".subject",
            ".tit",
            "strong",
            "h3",
            "h4",
        ]:
            title_element = block.select_one(selector)

            if title_element:
                candidate = clean_text(
                    title_element.get_text(" ", strip=True)
                )
                title, separated_content = split_title_content(candidate)

                if separated_content and not content:
                    content = separated_content

                if title:
                    break

    published_at = extract_date(full_text)
    views = extract_views(full_text)

    # 작성자 추출
    author = ""

    author_selectors = [
        ".writer",
        ".author",
        ".name",
        ".user",
    ]

    for selector in author_selectors:
        author_element = block.select_one(selector)

        if author_element:
            author = clean_text(
                author_element.get_text(" ", strip=True)
            )

            if author:
                break

    # 작성자 선택자를 못 찾았을 때 텍스트에서 추정
    if not author and published_at:
        date_position = full_text.find(published_at)
        before_date = full_text[:date_position].strip()

        # 제목뿐 아니라 분리된 내용도 제거한 뒤 작성자 후보를 찾습니다.
        for remove_text in [title, content]:
            if remove_text and before_date.startswith(remove_text):
                before_date = before_date[len(remove_text):].strip()
            elif remove_text:
                before_date = before_date.replace(remove_text, " ", 1).strip()

        before_date = re.sub(r"^[□■▪●◇◆]", "", before_date).strip()
        tokens = before_date.split()

        if tokens:
            candidate = tokens[-1]

            if (
                1 <= len(candidate) <= 15
                and not candidate.isdigit()
                and "조회수" not in candidate
            ):
                author = candidate

    # 링크에서 내용이 분리되지 않은 경우에만 별도 내용 태그를 찾습니다.
    if not content:
        content_selectors = [
            ".content",
            ".summary",
            ".cont",
            ".txt",
            ".description",
            "p",
        ]

        for selector in content_selectors:
            content_candidates = block.select(selector)
            cleaned_candidates = []

            for element in content_candidates:
                candidate_text = clean_text(
                    element.get_text(" ", strip=True)
                )

                if not candidate_text or candidate_text == title:
                    continue

                _, separated_content = split_title_content(candidate_text)
                if separated_content:
                    candidate_text = separated_content

                if published_at and candidate_text == published_at:
                    continue

                if "조회수" in candidate_text and len(candidate_text) < 80:
                    continue

                cleaned_candidates.append(candidate_text)

            if cleaned_candidates:
                content = max(cleaned_candidates, key=len)

                if len(content) >= 20:
                    break

    # 그래도 내용을 못 찾았을 때 전체 텍스트에서 제목과 메타정보를 제거
    if not content:
        content = full_text

        for remove_text in [title, author, published_at]:
            if remove_text:
                content = content.replace(remove_text, " ", 1)

        content = re.sub(r"조회수\s*[:：]?\s*[\d,]+", " ", content)
        content = re.sub(r"^[\s□■▪●◇◆]+", "", content)
        content = clean_text(content)

    return {
        "페이지": str(page_number),
        "제목": clean_text(title),
        "내용": clean_text(content),
        "작성자": clean_text(author),
        "등록일": clean_text(published_at),
        "조회수": clean_text(views),
    }


def crawl_current_page(
    driver: webdriver.Chrome,
    page_number: int,
) -> list[dict[str, str]]:
    """현재 브라우저에 열린 페이지의 게시물 목록을 추출합니다."""

    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    # 뉴스 제목 또는 조회수가 나타날 때까지 기다립니다.
    wait.until(
        lambda browser: "조회수" in browser.page_source
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    blocks = find_news_blocks(soup)

    if not blocks:
        raise ValueError(
            "게시물 목록을 찾지 못했습니다. "
            "사이트 구조 또는 선택자를 확인하세요."
        )

    page_data = []

    for block in blocks:
        news = parse_news_block(block, page_number)

        # 제목과 날짜가 둘 다 비어 있으면 잘못 잡힌 블록으로 판단
        if not news["제목"] and not news["등록일"]:
            continue

        page_data.append(news)

    # 같은 페이지 내 중복 제거
    unique_data = []
    seen = set()

    for item in page_data:
        key = (
            item["제목"],
            item["등록일"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_data.append(item)

    if not unique_data:
        raise ValueError(
            "게시물 블록은 찾았지만 유효한 데이터를 추출하지 못했습니다."
        )

    return unique_data


# =========================================================
# 6. 페이지 이동
# =========================================================
def click_page_link(
    driver: webdriver.Chrome,
    target_page: int,
) -> bool:
    """화면에 표시된 페이지 번호 링크를 클릭합니다."""

    xpath_candidates = [
        (
            "//a[normalize-space(text())="
            f"'{target_page}']"
        ),
        (
            "//button[normalize-space(text())="
            f"'{target_page}']"
        ),
        (
            "//*[self::a or self::button]"
            f"[normalize-space(.)='{target_page}']"
        ),
    ]

    for xpath in xpath_candidates:
        try:
            elements = driver.find_elements(By.XPATH, xpath)

            for element in elements:
                if not element.is_displayed():
                    continue

                driver.execute_script(
                    "arguments[0].scrollIntoView("
                    "{block: 'center'});",
                    element,
                )
                time.sleep(0.3)

                try:
                    element.click()
                except (
                    StaleElementReferenceException,
                    WebDriverException,
                ):
                    driver.execute_script(
                        "arguments[0].click();",
                        element,
                    )

                return True

        except WebDriverException:
            continue

    return False


def execute_page_script(
    driver: webdriver.Chrome,
    target_page: int,
) -> bool:
    """
    페이지 번호 링크를 직접 클릭하지 못할 때
    사이트의 JavaScript 페이지 이동 함수를 찾아 실행합니다.
    """

    script_names = [
        # 자동차리콜센터와 공공기관 사이트에서 자주 사용하는 함수명
        "fn_egov_link_page",
        "fnEgovLinkPage",
        "fnLinkPage",
        "fnSearch",
        "fnPage",
        "goPage",
        "movePage",
        "pageMove",
        "paging",
        "searchList",
        "fn_select_page",
        "linkPage",
    ]

    for function_name in script_names:
        try:
            exists = driver.execute_script(
                f"return typeof {function_name} === 'function';"
            )

            if not exists:
                continue

            driver.execute_script(
                f"{function_name}(arguments[0]);",
                target_page,
            )

            return True

        except WebDriverException:
            continue

    return False


def click_next_block(driver: webdriver.Chrome) -> bool:
    """다음 페이지 묶음 또는 다음 버튼을 클릭합니다."""

    xpath_candidates = [
        "//a[contains(normalize-space(.), '다음')]",
        "//button[contains(normalize-space(.), '다음')]",
        "//a[@title='다음']",
        "//a[contains(@class, 'next')]",
        "//button[contains(@class, 'next')]",
    ]

    for xpath in xpath_candidates:
        try:
            elements = driver.find_elements(By.XPATH, xpath)

            for element in elements:
                if not element.is_displayed():
                    continue

                driver.execute_script(
                    "arguments[0].scrollIntoView("
                    "{block: 'center'});",
                    element,
                )
                time.sleep(0.3)
                driver.execute_script(
                    "arguments[0].click();",
                    element,
                )

                return True

        except WebDriverException:
            continue

    return False


def move_to_page(
    driver: webdriver.Chrome,
    target_page: int,
) -> None:
    """원하는 페이지 번호로 이동합니다."""

    current_page = get_current_page(driver)

    if current_page == target_page:
        return

    previous_source = driver.page_source

    # 1. 화면에 대상 페이지 번호가 있으면 직접 클릭
    moved = click_page_link(driver, target_page)

    # 2. 페이지 함수가 있으면 실행
    if not moved:
        moved = execute_page_script(driver, target_page)

    # 3. 다음 페이지 묶음으로 이동한 후 다시 번호 클릭
    if not moved:
        moved = click_next_block(driver)

        if moved:
            WebDriverWait(driver, 20).until(
                lambda browser: (
                    browser.page_source != previous_source
                )
            )
            time.sleep(0.7)
            previous_source = driver.page_source
            moved = click_page_link(driver, target_page)

    if not moved:
        raise RuntimeError(
            f"{target_page}페이지로 이동할 버튼 또는 "
            "JavaScript 함수를 찾지 못했습니다."
        )

    # 페이지 내용이 바뀔 때까지 기다립니다.
    WebDriverWait(driver, 20).until(
        lambda browser: (
            browser.page_source != previous_source
        )
    )

    time.sleep(0.8)


# =========================================================
# 7. CSV 저장과 이어받기
# =========================================================
def load_existing_data() -> list[dict[str, str]]:
    """기존 CSV가 있으면 읽어옵니다."""

    if not OUTPUT_FILE.exists():
        return []

    try:
        df = pd.read_csv(
            OUTPUT_FILE,
            encoding="utf-8-sig",
            dtype=str,
        ).fillna("")

    except UnicodeDecodeError:
        df = pd.read_csv(
            OUTPUT_FILE,
            encoding="cp949",
            dtype=str,
        ).fillna("")

    for column in CSV_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[CSV_COLUMNS]

    return df.to_dict("records")


def get_start_page(
    existing_data: list[dict[str, str]],
) -> int:
    """기존 CSV의 마지막 페이지 다음 번호를 반환합니다."""

    if not existing_data:
        return 1

    pages = []

    for row in existing_data:
        page_text = clean_text(row.get("페이지", ""))

        if page_text.isdigit():
            pages.append(int(page_text))

    if not pages:
        return 1

    return max(pages) + 1


def save_data(data: list[dict[str, str]]) -> None:
    """현재까지 수집한 데이터를 CSV로 저장합니다."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.DataFrame(
        data,
        columns=CSV_COLUMNS,
    )

    # 제목과 등록일이 같은 데이터 중복 제거
    if not df.empty:
        df = df.drop_duplicates(
            subset=["제목", "등록일"],
            keep="first",
        )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )


# =========================================================
# 8. 메인 크롤링
# =========================================================
def main() -> None:
    """전체 크롤링을 실행합니다."""

    print("=" * 60)
    print("자동차 리콜 보도자료 크롤링 시작")
    print(f"저장 위치: {OUTPUT_FILE}")
    print("=" * 60)

    all_data = load_existing_data()
    start_page = get_start_page(all_data)

    if start_page > MAX_PAGES:
        print(
            "이미 설정된 마지막 페이지까지 수집했습니다."
        )
        return

    if all_data:
        print(
            f"기존 데이터 {len(all_data)}건을 불러왔습니다."
        )
        print(
            f"{start_page}페이지부터 이어서 시작합니다."
        )
    else:
        print("새로운 CSV 파일을 생성합니다.")

    driver = None

    try:
        driver = create_driver()
        driver.get(BASE_URL)

        WebDriverWait(driver, 20).until(
            lambda browser: "조회수" in browser.page_source
        )

        # 항상 1페이지에서 시작하여 순서대로 이동합니다.
        # 기존 CSV에 10페이지까지 저장되어 있으면,
        # 1~10페이지는 다시 저장하지 않고 화면만 넘긴 뒤
        # 11페이지부터 새 데이터를 저장합니다.
        for page_number in range(
            1,
            MAX_PAGES + 1,
        ):
            success = False

            for retry in range(
                1,
                MAX_RETRIES + 1,
            ):
                try:
                    print(
                        f"\n[{page_number}/{MAX_PAGES}] "
                        f"{page_number}페이지 수집 시작 "
                        f"(시도 {retry}/{MAX_RETRIES})"
                    )

                    # 현재 페이지와 목표 페이지가 다르면 이동
                    if get_current_page(driver) != page_number:
                        move_to_page(
                            driver,
                            page_number,
                        )

                    # 기존에 저장된 페이지는 다시 크롤링하지 않고 건너뜁니다.
                    if page_number < start_page:
                        print(
                            f"{page_number}페이지는 이미 저장되어 있어 "
                            "화면 이동만 하고 건너뜁니다."
                        )
                        success = True
                        time.sleep(0.5)
                        break

                    page_data = crawl_current_page(
                        driver,
                        page_number,
                    )

                    all_data.extend(page_data)
                    save_data(all_data)

                    print(
                        f"{page_number}페이지 "
                        f"{len(page_data)}건 수집 완료"
                    )
                    print(
                        f"현재까지 총 {len(all_data)}건 저장"
                    )

                    success = True
                    time.sleep(PAGE_DELAY)
                    break

                except (
                    TimeoutException,
                    StaleElementReferenceException,
                    ConnectionResetError,
                    WebDriverException,
                    RuntimeError,
                    ValueError,
                ) as error:
                    print(
                        f"{page_number}페이지 오류: "
                        f"{type(error).__name__}: {error}"
                    )

                    # 오류가 나도 현재까지 데이터는 저장
                    save_data(all_data)

                    if retry >= MAX_RETRIES:
                        break

                    print(
                        "브라우저를 다시 실행한 뒤 "
                        "재시도합니다."
                    )

                    try:
                        if driver is not None:
                            driver.quit()
                    except WebDriverException:
                        pass

                    time.sleep(3)

                    driver = create_driver()
                    driver.get(BASE_URL)

                    WebDriverWait(driver, 20).until(
                        lambda browser: (
                            "조회수" in browser.page_source
                        )
                    )

                    # 다음 시도에서 move_to_page가 실행됩니다.

            if not success:
                print(
                    f"\n{page_number}페이지를 "
                    f"{MAX_RETRIES}번 시도했지만 실패했습니다."
                )
                print(
                    "프로그램을 종료합니다. "
                    "다시 실행하면 저장된 다음 페이지부터 "
                    "이어갈 수 있습니다."
                )
                break

    except KeyboardInterrupt:
        print(
            "\n사용자가 Ctrl+C를 눌러 "
            "크롤링을 중단했습니다."
        )
        save_data(all_data)

    except Exception as error:
        print(
            "\n예상하지 못한 오류가 발생했습니다."
        )
        print(
            f"{type(error).__name__}: {error}"
        )
        save_data(all_data)

    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass

        print("\n현재까지 데이터 저장 완료")
        print(f"CSV 위치: {OUTPUT_FILE}")
        print("=" * 60)


if __name__ == "__main__":
    main()
