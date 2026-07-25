import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.services.geocoding import enrich_with_coords
from src.services.phone_format import format_phone

ROOT = Path(__file__).resolve().parents[2]

SAVE_PATH = ROOT / "crawled" / "bmw_service_centers.csv"

URL = "https://www.bmw.co.kr/ko/topics/owners/bmw-network/service_center.html"


def create_driver():
    """
    Selenium WebDriver 생성
    """
    options = Options()

    options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(
        service=service,
        options=options,
    )


def accept_cookie_banner(driver, timeout=15):
    """
    Shadow DOM 쿠키 동의 버튼 처리
    """

    script = """
    const host = document.querySelector('epaas-consent-drawer-shell');

    if (!host || !host.shadowRoot) {
        return false;
    }

    const btn = host.shadowRoot.querySelector(
        'button.accept-button'
    );

    if (!btn) {
        return false;
    }

    btn.click();

    return true;
    """

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            result = driver.execute_script(script)

            if result:
                return True

        except Exception:
            pass

        time.sleep(0.5)

    return False


def switch_dealer_iframe(driver):
    """
    BMW 서비스센터 iframe 이동
    """

    wait = WebDriverWait(driver, 30)

    iframe = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe[src*='bmw-dealer-locator']")
        )
    )

    driver.switch_to.frame(iframe)


def crawl_bmw_page(driver):
    """
    BMW 서비스센터 목록 크롤링
    """

    wait = WebDriverWait(driver, 30)

    items = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "content_area_choise_item"))
    )

    result = []

    for item in items:
        try:
            name_element = item.find_element(
                By.CLASS_NAME, "content_area_choise_item_anchor"
            )

            name = name_element.get_attribute("textContent").strip()

            desc = item.find_element(
                By.CSS_SELECTOR, "div.content_area_choise_info_desc"
            )

            left = desc.find_element(
                By.CLASS_NAME, "content_area_choise_info_desc_left"
            )

            desc_items = left.find_elements(
                By.CLASS_NAME, "content_area_choise_info_desc_item"
            )

            phone = None
            address = None

            for item in desc_items:
                text = item.get_attribute("textContent").strip()

                if "전화번호" in text:
                    phone = format_phone(text.replace("전화번호", ""))

                elif "신주소" in text:
                    address = text.replace("신주소", "").strip()

            result.append(
                {
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "company": "BMW",
                }
            )

        except Exception as e:
            print("파싱 실패:", e)

    return result


def parse_service_center(data):
    """
    BMW 데이터 규격 통일
    """

    return {
        "name": data.get("name"),
        "address": data.get("address"),
        "phone": data.get("phone"),
        "company": data.get("company"),
    }


def save_csv(data):

    df = pd.DataFrame(data)

    df.to_csv(
        SAVE_PATH,
        index=False,
        encoding="utf-8-sig",
    )


def main():

    driver = create_driver()

    try:
        driver.get(URL)

        if accept_cookie_banner(driver):
            print("쿠키 배너 처리 완료")

        switch_dealer_iframe(driver)

        raw_data = crawl_bmw_page(driver)

        service_center_data = [parse_service_center(item) for item in raw_data]

        # 주소 기반 좌표 추가
        service_center_data = enrich_with_coords(
            service_center_data,
            address_key="address",
            name_key="name",
        )

        save_csv(service_center_data)

        print(f"BMW 서비스센터 {len(service_center_data)}건 저장 완료")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
