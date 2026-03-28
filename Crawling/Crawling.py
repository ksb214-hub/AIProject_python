from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

from Crawling.driver import get_driver
from Utils.text_clean import clean_text

def crawl(search):

    driver = get_driver()

    base_url = "https://www.10000recipe.com/recipe/list.html?q="
    driver.get(base_url + search)
    time.sleep(2)

    recipe_list = driver.find_elements(By.CSS_SELECTOR, "#contents_area_full > ul > ul > li")

    titles = []
    urls = []

    for item in recipe_list:
        try:
            href = item.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href")
            title = item.find_element(
                By.CSS_SELECTOR,
                "div.common_sp_caption > div.common_sp_caption_tit.line2"
            ).text.strip()

            titles.append(title)
            urls.append(href)

        except:
            continue

    all_data = []

    while True:
        print("\n=== 레시피 목록 ===")
        for i, t in enumerate(titles):
            print(f"[{i+1}] {t}")

        print("[0] 종료 / [auto] 자동수집")

        choice = input("입력: ")

        if choice == "0":
            break

        elif choice == "auto":
            for i in range(min(5, len(urls))):
                driver.get(urls[i])
                time.sleep(1)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                ingredients = soup.select("#divConfirmedMaterialArea > ul:nth-child(1) > li")

                for ing in ingredients:
                    text = clean_text(ing.get_text(strip=True))
                    if text:
                        all_data.append([titles[i], text])

        else:
            idx = int(choice) - 1

            driver.get(urls[idx])
            time.sleep(1)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            ingredients = soup.select("#divConfirmedMaterialArea > ul:nth-child(1) > li")

            for ing in ingredients:
                text = clean_text(ing.get_text(strip=True))
                if text:
                    all_data.append([titles[idx], text])

    driver.quit()

    df = pd.DataFrame(all_data, columns=["레시피", "재료"])
    return df