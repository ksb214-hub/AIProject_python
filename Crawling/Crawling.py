from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

def crawl_recipe(search):
    # 1. driver 셋팅
    driver = webdriver.Chrome()
    
    # 2. URL 접속
    url = "https://www.10000recipe.com/recipe/list.html?q="
    driver.get(url + search)
    time.sleep(2)

    try:
        # 3. 레시피 개수 파싱
        count_element = driver.find_element(By.CSS_SELECTOR, "#contents_area_full > ul > div > b")
        recipe_count = int(count_element.text.replace(",", ""))

        print(f"검색된 레시피 개수: {recipe_count}")

        # 4. 레시피가 1개 이상일 경우
        if recipe_count > 0:
            first_recipe = driver.find_element(
                By.CSS_SELECTOR,
                "#contents_area_full > ul > ul > li:nth-child(1) > div.common_sp_thumb > a"
            )

            href = first_recipe.get_attribute("href")
            text = first_recipe.get_attribute("title")

            print("첫 번째 레시피 URL:", href)
            print("첫 번째 레시피 제목:", text)

        # 5. 레시피가 없는 경우
        else:
            print("해당 레시피가 존재하지 않습니다.")

    except Exception as e:
        print("오류 발생:", e)

    finally:
        driver.quit()


# 실행 테스트
if __name__ == "__main__":
    search = input("검색어를 입력하세요: ")
    crawl_recipe(search)