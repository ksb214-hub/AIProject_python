from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def crawl_recipe(search):
    # 2. driver 셋팅 (백그라운드 실행)
    options = Options()
    options.add_argument("--headless")  # 창 안 띄움
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    base_url = "https://www.10000recipe.com/recipe/list.html?q="
    detail_base_url = "https://www.10000recipe.com"

    # 3. 검색 페이지 접속
    driver.get(base_url + search)
    time.sleep(2)

    try:
        # 4. 레시피 개수 파싱
        count_element = driver.find_element(By.CSS_SELECTOR, "#contents_area_full > ul > div > b")
        recipe_count = int(count_element.text.replace(",", ""))

        print(f"레시피 개수: {recipe_count}")

        # 5. 레시피가 1개 이상일 경우
        if recipe_count > 0:

            recipe_list = driver.find_elements(
                By.CSS_SELECTOR,
                "#contents_area_full > ul > ul > li"
            )

            urls = []

            # 5-1. for문
            for item in recipe_list:
                try:
                    a_tag = item.find_element(By.CSS_SELECTOR, "div > a")
                    href = a_tag.get_attribute("href")
                    urls.append(href)
                except:
                    continue

            # 6. 첫 번째 URL 출력
            if urls:
                first_url = urls[0]
                print("첫 번째 레시피 URL:", first_url)

                # 7. 상세 페이지 이동
                if first_url.startswith("http"):
                    detail_url = first_url
                else:
                    detail_url = detail_base_url + first_url

                driver.get(detail_url)
                time.sleep(2)

        # 5-2. 레시피가 없는 경우
        else:
            print("해당 레시피가 존재하지 않습니다.")

    except Exception as e:
        print("오류 발생:", e)

    finally:
        # 8. driver 종료
        driver.quit()


# 실행
if __name__ == "__main__":
    search = input("검색어 입력: ")
    crawl_recipe(search)