from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# =========================================================
# [1] 텍스트 정제 함수
# - '구매' 제거
# - 숫자 제거 (용량 제거)
# - 공백 정리
# =========================================================
def clean_text(text):
    text = text.replace("구매", "").strip()        # 불필요 단어 제거
    text = re.split(r"\d", text)[0].strip()        # 숫자 제거 (ex: 200g)
    text = re.sub(r"\s+", " ", text)              # 공백 정리
    return text


# =========================================================
# [2] 추천 시스템 함수
# - 사용자 재료 vs 레시피 재료 비교
# - 겹치는 비율로 점수 계산
# =========================================================
def recommend_recipe(df, user_ingredients):

    recipe_scores = {}

    # 레시피별 재료 묶기
    recipe_group = df.groupby("레시피")["재료"].apply(list)

    for recipe, ingredients in recipe_group.items():

        # 교집합 → 겹치는 재료
        match_count = len(set(user_ingredients) & set(ingredients))

        # 전체 재료 개수
        total_count = len(ingredients)

        # 유사도 계산
        score = match_count / total_count if total_count > 0 else 0

        recipe_scores[recipe] = score

    # 점수 기준 정렬
    sorted_recipes = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_recipes


# =========================================================
# [3] 메인 크롤링 함수
# 전체 흐름:
# 검색 → 리스트 수집 → 선택 → 상세 → 재료 추출 → 누적 → 추천
# =========================================================
def crawl_recipe(search):

    # -----------------------------------------------------
    # [3-1] driver 설정 (백그라운드 실행)
    # -----------------------------------------------------
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    base_url = "https://www.10000recipe.com/recipe/list.html?q="

    # -----------------------------------------------------
    # [3-2] 검색 페이지 접속
    # -----------------------------------------------------
    driver.get(base_url + search)
    time.sleep(2)

    try:
        # -------------------------------------------------
        # [3-3] 레시피 리스트 수집
        # -------------------------------------------------
        recipe_list = driver.find_elements(By.CSS_SELECTOR, "#contents_area_full > ul > ul > li")

        titles = []
        urls = []

        for item in recipe_list:
            try:
                # URL 수집
                href = item.find_element(By.CSS_SELECTOR, "div > a").get_attribute("href")

                # 제목 수집
                title = item.find_element(
                    By.CSS_SELECTOR,
                    "div.common_sp_caption > div.common_sp_caption_tit.line2"
                ).text.strip()

                titles.append(title)
                urls.append(href)

            except:
                continue

        # -------------------------------------------------
        # [3-4] 누적 데이터 저장 리스트
        # -------------------------------------------------
        all_selected_data = []

        # -------------------------------------------------
        # [3-5] 반복 선택 루프
        # -------------------------------------------------
        while True:

            # -----------------------------
            # 레시피 목록 출력
            # -----------------------------
            print("\n=== 레시피 목록 ===")
            for i, t in enumerate(titles):
                print(f"[{i+1}] {t}")

            print("\n[0] 종료")
            print("[auto] 자동 수집")

            choice = input("\n번호 입력: ")

            # -----------------------------
            # 종료 조건
            # -----------------------------
            if choice == "0":
                print("프로그램 종료")
                break

            # -----------------------------
            # 자동 수집 모드
            # -----------------------------
            elif choice == "auto":

                print("\n자동 수집 시작...")

                for i in range(min(5, len(urls))):

                    driver.get(urls[i])
                    time.sleep(1)

                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    ingredients = soup.select("#divConfirmedMaterialArea > ul:nth-child(1) > li")

                    for ing in ingredients:
                        text = clean_text(ing.get_text(strip=True))

                        if text:
                            # 레시피 + 재료 형태로 저장
                            all_selected_data.append([titles[i], text])

                print("자동 수집 완료")

            # -----------------------------
            # 개별 선택 모드
            # -----------------------------
            else:
                try:
                    idx = int(choice) - 1

                    # 범위 체크
                    if idx < 0 or idx >= len(urls):
                        print("잘못된 입력")
                        continue

                    driver.get(urls[idx])
                    time.sleep(1)

                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    ingredients = soup.select("#divConfirmedMaterialArea > ul:nth-child(1) > li")

                    ingredient_list = []

                    for ing in ingredients:
                        text = clean_text(ing.get_text(strip=True))

                        if text:
                            ingredient_list.append(text)

                            # 누적 저장
                            all_selected_data.append([titles[idx], text])

                    # 결과 출력
                    df = pd.DataFrame(ingredient_list, columns=["재료"])

                    print(f"\n=== {titles[idx]} 재료 ===")
                    print(df)

                except:
                    print("입력 오류")

        # -------------------------------------------------
        # [3-6] 전체 데이터 DataFrame 변환
        # -------------------------------------------------
        final_df = pd.DataFrame(all_selected_data, columns=["레시피", "재료"])

        print("\n=== 전체 데이터 ===")
        print(final_df)

        # -------------------------------------------------
        # [3-7] 추천 시스템 실행
        # -------------------------------------------------
        user_input = input("\n보유 재료 입력 (쉼표로 구분): ")
        user_ingredients = [i.strip() for i in user_input.split(",")]

        result = recommend_recipe(final_df, user_ingredients)

        print("\n=== 추천 결과 ===")
        for recipe, score in result[:5]:
            print(f"{recipe} (유사도: {score:.2f})")

    except Exception as e:
        print("오류:", e)

    finally:
        # -------------------------------------------------
        # [3-8] driver 종료
        # -------------------------------------------------
        driver.quit()


# =========================================================
# [4] 프로그램 시작
# =========================================================
if __name__ == "__main__":
    search = input("검색어 입력: ")
    crawl_recipe(search)