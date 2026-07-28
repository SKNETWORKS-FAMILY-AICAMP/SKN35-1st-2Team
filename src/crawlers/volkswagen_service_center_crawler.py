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
SAVE_PATH = ROOT / "crawled" / "volkswagen_service_centers.csv"

options = Options()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
url = "https://www.volkswagen.co.kr/app/locals/information/map/servicecenter.jsp"

driver.get(url)

wait = WebDriverWait(driver, 20)
accordion_item = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "accordion-item"))
)

volkswagen_crawling_list = []

for item in accordion_item:
    volkswagen_crawling_dict = {}
    header_item = item.find_element(By.CLASS_NAME, "header-item")
    header_address = header_item.find_element(By.CLASS_NAME, "address")
    header_dealer = header_item.find_element(By.CLASS_NAME, "dealer")

    volkswagen_crawling_dict["address"] = header_address.text
    volkswagen_crawling_dict["name"] = header_dealer.text

    header_button = item.find_element(By.CLASS_NAME, "accordion-btn")

    header_button.click()

    wait.until(
        lambda d: item.find_element(By.CLASS_NAME, "infor-wrap").text.strip() != ""
    )

    panel_item = item.find_element(By.CLASS_NAME, "infor-wrap")

    panel_text_wrap = panel_item.find_elements(By.CLASS_NAME, "text-wrap")
    volkswagen_crawling_dict["phone"] = panel_text_wrap[1].text

    volkswagen_crawling_dict["company"] = "폭스바겐"

    volkswagen_crawling_list.append(volkswagen_crawling_dict)

    time.sleep(1)


volkswagen_service_center_data = enrich_with_coords(
    volkswagen_crawling_list,
    address_key="address",
    name_key="name",
)
df = pd.DataFrame(volkswagen_service_center_data)

df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")
