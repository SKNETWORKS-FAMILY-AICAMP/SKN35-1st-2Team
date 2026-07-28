# volkswagen 서비스 센터 crawler

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

from src.utils.geocoding import enrich_with_coords
from src.utils.phone_format import format_phone

ROOT = Path(__file__).resolve().parents[3]

SAVE_PATH = ROOT / "crawled" / "volkswagen_service_centers.csv"

URL = "https://www.volkswagen.co.kr/app/locals/information/map/servicecenter.jsp"


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


def crawl_volkswagen_page(driver):
    """
    폭스바겐 서비스센터 크롤링
    """

    wait = WebDriverWait(driver, 30)

    accordion_items = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "accordion-item"))
    )

    result = []

    for index, item in enumerate(accordion_items, start=1):
        try:
            header_item = item.find_element(By.CLASS_NAME, "header-item")

            address = header_item.find_element(By.CLASS_NAME, "address").text.strip()

            name = header_item.find_element(By.CLASS_NAME, "dealer").text.strip()

            button = item.find_element(By.CLASS_NAME, "accordion-btn")

            driver.execute_script("arguments[0].click();", button)

            wait.until(
                lambda d: (
                    item.find_element(By.CLASS_NAME, "infor-wrap").text.strip() != ""
                )
            )

            info_wrap = item.find_element(By.CLASS_NAME, "infor-wrap")

            text_wraps = info_wrap.find_elements(By.CLASS_NAME, "text-wrap")

            phone = None

            if len(text_wraps) > 1:
                phone = format_phone(text_wraps[1].text)

            result.append(
                {
                    "name": name,
                    "address": address,
                    "phone": phone,
                }
            )

            print(f"[{index}/{len(accordion_items)}] 저장 : {name}")

            time.sleep(0.5)

        except Exception as e:
            print(f"[{index}] 크롤링 실패:", e)

    return result


def parse_service_center(data):
    """
    CSV 규격 통일
    """

    return {
        "name": data.get("name"),
        "address": data.get("address"),
        "phone": data.get("phone"),
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

        raw_data = crawl_volkswagen_page(driver)

        service_center_data = [parse_service_center(item) for item in raw_data]

        service_center_data = enrich_with_coords(
            service_center_data,
            address_key="address",
            name_key="name",
        )

        save_csv(service_center_data)

        print(f"\n폭스바겐 서비스센터 {len(service_center_data)}건 저장 완료")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
