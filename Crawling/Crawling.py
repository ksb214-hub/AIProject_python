# Crawling/Crawling.py
# 이 파일은 프로젝트의 **'컨트롤러'**입니다. 
# 위 라이브러리들을 사용하여 실제로 웹사이트에 접속하고 데이터를 리스트화합니다.

# [표준 라이브러리]
# time: 웹 페이지 로딩 대기 및 프로세스 간격 조절을 위한 시간 제어 모듈
import time

# [제3자 라이브러리 (External)]
# BeautifulSoup: Selenium이 가져온 HTML 소스코드를 계층 구조로 파싱하여 데이터 추출을 돕는 도구
from bs4 import BeautifulSoup

# ThreadPoolExecutor: 멀티스레딩 구현을 위한 실행기. 여러 브라우저를 동시에 띄워 수집 속도를 극대화함
# as_completed: 생성된 스레드 작업들 중 먼저 완료된 순서대로 결과를 반환받기 위한 반복자(Iterator)
from concurrent.futures import ThreadPoolExecutor, as_completed

# [내부 모듈 (Internal Libraries)]
# driver_loader: 프로젝트 전용 Selenium WebDriver 설정 및 생성 라이브러리 (공통 엔진)
from driver.driver_loader import get_headless_driver

# data_processor: 수집된 텍스트에서 불필요한 단어('구매' 등)를 정규표현식으로 제거하는 정제 도구
from utils.data_processor import DataCleaner

# data_frame_factory: 수집된 리스트 데이터를 Pandas DataFrame으로 변환 및 관리하는 데이터 전담 모듈
from processing.data_frame_factory import RecipeDataManager


class RecipeCrawler:
    """
    [설계 의도: 고성능 병렬 스크래핑 컨트롤러]
    - 목록은 단일 드라이버로 빠르게, 상세 페이지는 멀티스레드로 동시 수집합니다.
    """
    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        self.cleaner = DataCleaner()
        self.driver = None # 메인 드라이버 참조용 (에러 방지)

    def fetch_recipe_list(self):
        """[흐름: 검색어 입력 -> 목록 페이지 접속 -> 제목/URL 리스트화]"""
        list_driver = get_headless_driver()
        try:
            keyword = input("어떤 레시피를 검색할까요? : ")
            search_url = f"{self.base_url}/recipe/list.html?q={keyword}"
            list_driver.get(search_url)
            time.sleep(1.5)

            soup = BeautifulSoup(list_driver.page_source, 'html.parser')
            
            # 레시피 개수 확인 (Selector: #contents_area_full > ul > div > b)
            count_tag = soup.select_one('#contents_area_full > ul > div > b')
            if not count_tag or count_tag.get_text().strip() == '0':
                print(f"'{keyword}' 검색 결과가 없습니다.")
                return [], []

            # 레시피 카드 요소 추출
            recipe_items = soup.select('#contents_area_full > ul > ul > li')
            titles, urls = [], []

            for item in recipe_items:
                title_el = item.select_one('div.common_sp_caption_tit.line2')
                link_el = item.select_one('a.common_sp_link')
                if title_el and link_el:
                    titles.append(self.cleaner.clean_title(title_el.get_text()))
                    urls.append(self.base_url + link_el['href'])
            
            return titles, urls
        finally:
            list_driver.quit() # 목록 수집용 드라이버 즉시 종료

    def fetch_recipe_detail_worker(self, title, url):
        """[스레드 작업 유닛: 각 상세 페이지 접속 및 데이터 추출]"""
        worker_driver = get_headless_driver()
        try:
            worker_driver.get(url)
            time.sleep(1.2)
            soup = BeautifulSoup(worker_driver.page_source, 'html.parser')
            
            # 이미지 및 재료 데이터 추출
            img_tag = soup.select_one('#main_thumbs')
            image_url = img_tag['src'] if img_tag else "이미지 없음"
            
            material_tags = soup.select('#divConfirmedMaterialArea > ul:nth-child(1) > li')
            materials = [self.cleaner.clean_material(mat.get_text(separator=' ', strip=True)) 
                         for mat in material_tags if mat]
            
            return {"title": title, "url": url, "image": image_url, "materials": materials}
        except Exception as e:
            print(f"❌ 수집 오류 [{title}]: {e}")
            return None
        finally:
            worker_driver.quit() # 스레드 종료 시 브라우저 강제 종료 (메모리 확보)

    def collect_parallel(self, titles, urls, max_workers=4):
        """[ThreadPoolExecutor를 통한 병렬 처리 실행]"""
        final_collection = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 작업 할당
            futures = {executor.submit(self.fetch_recipe_detail_worker, titles[i], urls[i]): i for i in range(len(urls))}
            
            # 완료된 순서대로 결과 취합
            for future in as_completed(futures):
                result = future.result()
                if result:
                    final_collection.append(result)
                    print(f"✅ 완료: {result['title']}")
        return final_collection

# --- 메인 실행부 ---
if __name__ == "__main__":
    crawler = RecipeCrawler()
    
    try:
        # 1. 목록 수집
        t_list, u_list = crawler.fetch_recipe_list()
        
        if t_list:
            # 2. 병렬 상세 수집 (동시 4개 브라우저 가동)
            raw_data = crawler.collect_parallel(t_list, u_list, max_workers=4)
            
            # 3. 데이터 가공 및 결과 출력 (Processing 모듈 호출)
            manager = RecipeDataManager(raw_data)
            manager.process_to_dataframe()
            
    except Exception as e:
        print(f"❗ 시스템 오류 발생: {e}")
# --- 메인 실행부 ---
if __name__ == "__main__":
    crawler = RecipeCrawler()
    
    try:
        # 1. 목록 가져오기
        recipe_titles, recipe_urls = crawler.fetch_recipe_list()
        
        if recipe_titles:
            # 2. 병렬로 상세 데이터 수집 (사양에 따라 max_workers 조절 가능)
            # 맥북 프로 환경이므로 4~6 정도를 추천합니다.
            raw_details = crawler.collect_all_details(recipe_titles, recipe_urls, max_workers=4)
            
            # 3. 데이터 가공 모듈 호출 (Processing/DataProcessor.py)
            manager = RecipeDataManager(raw_details)
            processed_df = manager.process_to_dataframe()
            
            if processed_df is not None:
                print("\n✨ 모든 작업이 완료되었습니다.")
                # 필요시 여기서 manager.save_csv() 호출 가능
                
    except Exception as e:
        print(f"❗ 메인 로직 실행 중 오류 발생: {e}")