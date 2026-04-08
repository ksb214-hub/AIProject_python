# Crawling/Crawling.py
# 이 파일은 프로젝트의 **'컨트롤러'**이자 **'메인 엔트리 포인트'**입니다.

import time
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# [내부 모듈 임포트]
from driver.driver_loader import get_headless_driver
from utils.data_processor import DataCleaner
from processing.data_frame_factory import RecipeDataManager
# Recipe 폴더 내의 챗봇 모듈 임포트
from Recipe.RecipeChatBot import run_recipe_chatbot

class RecipeCrawler:
    """
    [역할: 고성능 병렬 레시피 수집 컨트롤러]
    1. 목록 스캔 -> 2. 병렬 수집 -> 3. 정제 및 가공 -> 4. 챗봇 서비스 연결
    """

    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        self.cleaner = DataCleaner()

    def fetch_recipe_list(self):
        """목록 페이지 접속 및 레시피 URL 리스트 확보"""
        list_driver = get_headless_driver()
        try:
            keyword = input("어떤 레시피를 검색할까요? : ")
            search_url = f"{self.base_url}/recipe/list.html?q={keyword}"
            
            print(f"📡 '{keyword}' 검색 결과 페이지에 접속 중...")
            list_driver.get(search_url)
            time.sleep(1.5)

            soup = BeautifulSoup(list_driver.page_source, 'html.parser')
            count_tag = soup.select_one('#contents_area_full > ul > div > b')
            
            if not count_tag or count_tag.get_text().strip() == '0':
                print(f"⚠️ '{keyword}'에 대한 검색 결과가 없습니다.")
                return [], []

            recipe_items = soup.select('#contents_area_full > ul > ul > li')
            titles, urls = [], []

            for item in recipe_items:
                title_el = item.select_one('div.common_sp_caption_tit.line2')
                link_el = item.select_one('a.common_sp_link')
                
                if title_el and link_el:
                    clean_title = self.cleaner.clean_title(title_el.get_text())
                    full_url = self.base_url + link_el['href']
                    titles.append(clean_title)
                    urls.append(full_url)
            
            print(f"✅ 총 {len(titles)}개의 레시피 후보를 발견했습니다.")
            return titles, urls
        finally:
            list_driver.quit()

    def fetch_recipe_detail_worker(self, title, url):
        """개별 상세 페이지 수집 (스레드 단위 작업)"""
        worker_driver = get_headless_driver()
        try:
            worker_driver.get(url)
            time.sleep(1.2)
            soup = BeautifulSoup(worker_driver.page_source, 'html.parser')
            
            img_tag = soup.select_one('#main_thumbs')
            image_url = img_tag['src'] if img_tag else "이미지 없음"
            
            material_tags = soup.select('#divConfirmedMaterialArea > ul:nth-child(1) > li')
            origin_mats, pure_mats = [], []

            for mat in material_tags:
                raw_text = mat.get_text(separator=' ', strip=True)
                c_text = self.cleaner.clean_material(raw_text)
                p_text = self.cleaner.extract_pure_material(c_text)
                if c_text: origin_mats.append(c_text)
                if p_text: pure_mats.append(p_text)

            step_container = soup.select_one('#obx_recipe_step_start')
            recipe_steps = []
            if step_container:
                step_list = step_container.select('.view_step_cont')
                for idx, step in enumerate(step_list, 1):
                    step_text = step.get_text(strip=True)
                    if step_text:
                        clean_step = self.cleaner.clean_title(step_text)
                        recipe_steps.append(f"{idx}. {clean_step}")

            return {
                "title": title, "url": url, "image": image_url,
                "materials": origin_mats, "pure_materials": pure_mats, "steps": recipe_steps
            }
        except Exception as e:
            print(f"❌ 수집 실패 [{title}]: {e}")
            return None
        finally:
            worker_driver.quit()

    def collect_parallel(self, titles, urls, max_workers=4):
        """병렬 수집 실행 및 결과 취합"""
        final_collection = []
        print(f"🚀 병렬 수집 시작 (작업 스레드: {max_workers})...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.fetch_recipe_detail_worker, titles[i], urls[i]): i for i in range(len(urls))}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    final_collection.append(result)
                    print(f"✅ 수집 완료: {result['title']}")
        return final_collection

# --- [Main Execution Flow] ---
if __name__ == "__main__":
    crawler = RecipeCrawler()
    
    try:
        # [Step 1] 레시피 목록 확보
        recipe_titles, recipe_urls = crawler.fetch_recipe_list()
        
        if recipe_titles:
            # [Step 2] 상세 정보 병렬 크롤링 (상위 40개 기준)
            raw_dataset = crawler.collect_parallel(recipe_titles, recipe_urls, max_workers=4)
            
            # [Step 3] 데이터 가공 및 정형화 (Pandas DataFrame)
            manager = RecipeDataManager(raw_dataset)
            processed_df = manager.process_to_dataframe()
            
            if processed_df is not None and not processed_df.empty:
                # --- [출력 옵션 설정] ---
                pd.set_option('display.max_columns', None)
                pd.set_option('display.unicode.east_asian_width', True)
                pd.set_option('display.width', 1000)
                pd.set_option('display.max_colwidth', 30)

                print("\n" + "✨" * 30)
                print("   데이터 수집 및 가공이 완료되었습니다.")
                print("✨" * 30)

                # [요약 보고]
                print(f"\n📊 데이터 요약: 총 {len(processed_df)}개의 레시피 확보")
                print(f"🔎 샘플 확인: {processed_df[['title', 'pure_materials_str']].head(3)}")

                # [Step 4] AI 챗봇 실행
                # 가공된 데이터를 RecipeChatBot.py의 실행 함수로 전달합니다.
                print("\n🤖 AI 챗봇 학습 및 가동을 시작합니다. 잠시만 기다려 주세요...")
                run_recipe_chatbot(processed_df)

            else:
                print("❌ 가공할 데이터가 확보되지 않았습니다.")
        else:
            print("⚠️ 검색 결과가 없어 프로그램을 종료합니다.")

    except Exception as e:
        print(f"❗ 메인 로직 실행 중 오류 발생: {e}")