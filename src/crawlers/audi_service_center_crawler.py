import os
import random
import time

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.services.geocoding import enrich_with_coords

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

options = Options()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)
url = "https://www.audi.co.kr/ko/service/service-center/"
driver.get(url)

wait = WebDriverWait(driver, 20)

time.sleep(random.uniform(5, 7))

accordion = wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[data-testid='audi-accordion']")
    )
)

region_list = accordion.find_elements(By.CSS_SELECTOR, ":scope > span")

service_center_data = []

for region_index in range(len(region_list)):
    region_list = accordion.find_elements(By.CSS_SELECTOR, ":scope > span")

    button = region_list[region_index].find_element(By.TAG_NAME, "button")

    region_name = button.find_element(By.TAG_NAME, "span").text

    button.click()

    time.sleep(1)

    section_id = button.get_attribute("aria-controls")

    section = wait.until(EC.presence_of_element_located((By.ID, section_id)))

    service_links = section.find_elements(By.CSS_SELECTOR, "ul li a")

    for service_index in range(len(service_links)):
        section = driver.find_element(By.ID, section_id)

        service_links = section.find_elements(By.CSS_SELECTOR, "ul li a")

        service = service_links[service_index]

        service_name = service.text

        print(f"[진행중] {region_name} - {service_name}")

        service.click()

        try:
            modal = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".BasicTeaser__StyledTextArea-sc-f76fc4da-3.iAySJt",
                    )
                )
            )
        except Exception:
            print(f"[실패] {region_name} - {service_name}")
            print("현재 URL:", driver.current_url)
            os.makedirs("debug", exist_ok=True)
            driver.save_screenshot(f"debug/{region_name}_{service_name}.png")
            with open(
                f"debug/{region_name}_{service_name}.html", "w", encoding="utf-8"
            ) as f:
                f.write(driver.page_source)
            raise

        title = modal.find_element(By.TAG_NAME, "h2").text

        info_element = modal.find_element(
            By.CSS_SELECTOR, ".RichText__StyledText-sc-b2aa9242-0"
        )

        info = info_element.text

        address = ""
        tel = ""
        email = ""

        for line in info.split("\n"):
            if line.startswith("주소:"):
                address = line.replace("주소:", "").strip()

            elif line.startswith("Tel:"):
                tel = line.replace("Tel:", "").strip()

            elif line.startswith("E-mail:"):
                email = line.replace("E-mail:", "").strip()

        link = ""

        try:
            link = modal.find_element(By.CSS_SELECTOR, "a.button").get_attribute("href")

        except:
            pass

        data = {
            "지역": region_name,
            "센터명": title,
            "주소": address,
            "전화번호": tel,
            "이메일": email,
            "홈페이지": link,
        }

        service_center_data.append(data)

        close_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='one-layer-close']")
            )
        )

        close_button.click()

        wait.until(EC.invisibility_of_element(modal))

        time.sleep(random.uniform(1, 2))

print("crawling 완료")

service_center_data = enrich_with_coords(
    service_center_data,
    address_key="주소",
    name_key="센터명",
)

df = pd.DataFrame(service_center_data)
os.makedirs("../crawled", exist_ok=True)
df.to_csv("../crawled/audi_service_centers.csv", index=False, encoding="utf-8-sig")

print("파일 생성 완료")
