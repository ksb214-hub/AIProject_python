from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def crawl_recipe(search):
    # 1. driver 셋팅 (요즘 selenium은 자동 driver 지원됨)
    driver = webdriver.Chrome()

    # 2. 첫 번째 URL
    base_url = "https://www.10000recipe.com/recipe/list.html?q="
    detail_base_url = "https://www.10000recipe.com"

    # 3. 검색 페이지 접속
    driver.get(base_url + search)
    time.sleep(2)

    try:
        # 4. 레시피 개수 파싱
        count_element = driver.find_element(By.CSS_SELECTOR, "#contents_area_full > ul > div > b")
        recipe_count = int(count_element.text.replace(",", ""))

        print(f"검색된 레시피 개수: {recipe_count}")

        # 5. 레시피가 1개 이상일 경우
        if recipe_count > 0:
            first_recipe = driver.find_element(
                By.CSS_SELECTOR,
                "#contents_area_full > ul > ul > li:nth-child(1) > div.common_sp_thumb > a"
            )

            href = first_recipe.get_attribute("href")
            title = first_recipe.get_attribute("title")

            print("첫 번째 레시피 제목:", title)
            print("첫 번째 레시피 URL:", href)

            # 6. 상세 페이지 이동
            # href가 절대경로면 그대로 사용
            if href.startswith("http"):
                detail_url = href
            else:
                detail_url = detail_base_url + href

            print("상세 페이지 이동:", detail_url)

            driver.get(detail_url)
            time.sleep(2)

        # 5-2. 레시피가 없는 경우
        else:
            print("해당 레시피가 존재하지 않습니다.")

    except Exception as e:
        print("오류 발생:", e)

    finally:
        # 7. driver 종료 (맨 마지막)
        driver.quit()


# 실행
if __name__ == "__main__":
    search = input("검색어 입력: ")
    crawl_recipe(search)