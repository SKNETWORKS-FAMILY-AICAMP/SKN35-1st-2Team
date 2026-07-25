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

ROOT = Path(__file__).resolve().parents[2]
SAVE_PATH = ROOT / "crawled" / "bmw_service_centers.csv"


options = Options()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
url = "https://www.bmw.co.kr/ko/topics/owners/bmw-network/service_center.html"

driver.get(url)

wait = WebDriverWait(driver, 30)


def accept_cookie_banner(driver, timeout=15):
    """Shadow DOM 안의 쿠키 배너 accept 버튼을 JS로 찾아서 클릭"""
    script = """
    const host = document.querySelector('epaas-consent-drawer-shell');
    if (!host || !host.shadowRoot) return null;
    const btn = host.shadowRoot.querySelector('button.accept-button');
    if (!btn) return null;
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


if accept_cookie_banner(driver):
    print("쿠키 배너 수락 완료")
else:
    print("쿠키 배너를 찾지 못함 (이미 처리됐거나 안 뜬 경우)")


iframe = wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "iframe[src*='bmw-dealer-locator']")
    )
)
driver.switch_to.frame(iframe)


li_list = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "content_area_choise_item"))
)

bmw_crawling_list = []

for item in li_list:
    a = item.find_element(By.CLASS_NAME, "content_area_choise_item_anchor")
    name = a.get_attribute("textContent").strip()
    desc = item.find_element(By.CSS_SELECTOR, "div.content_area_choise_info_desc")
    left = desc.find_element(By.CLASS_NAME, "content_area_choise_info_desc_left")
    desc_items = left.find_elements(By.CLASS_NAME, "content_area_choise_info_desc_item")

    phone, address = None, None
    for di in desc_items:
        text = di.get_attribute("textContent").strip()
        if "전화번호" in text:
            phone = text.replace("전화번호", "").strip().replace(")", "-")
        elif "신주소" in text:
            address = text.replace("신주소", "").strip()

    bmw_crawling_list.append(
        {"name": name, "phone": phone, "address": address, "company": "bmw"}
    )

bmw_service_center_data = enrich_with_coords(
    bmw_crawling_list, address_key="address", name_key="name"
)

df = pd.DataFrame(bmw_service_center_data)

df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
