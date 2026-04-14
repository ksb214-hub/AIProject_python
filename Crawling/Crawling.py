import time
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# [내부 모듈 연결]
# 시니어 팁: 모듈화된 프로젝트에서는 경로 설정이 중요합니다.
from driver.driver_loader import get_headless_driver
from utils.data_processor import DataCleaner
from processing.data_frame_factory import RecipeDataManager

# [데이터 기획: 서비스의 뼈대가 될 핵심 카테고리]
# 배민처럼 사용자가 자주 찾는 키워드를 미리 정의하여 DB의 초기 신뢰도를 높입니다.
CATEGORIES = ["한식", "중식", "일식", "양식", "찌개", "고기", "분식", "디저트", "치킨"]

class RecipeCrawler:
    """
    [역할: 하이브리드 데이터 수집 컨트롤러]
    1. 정기적 대량 수집(Batch)과 실시간 핀포인트 수집(On-demand)을 모두 수행합니다.
    2. 수집된 데이터를 즉시 DB에 쌓아 메모리 효율을 극대화합니다.
    """

    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        self.cleaner = DataCleaner()
        self.db_path = 'recipes.db'

    # --- [내부 로직 1: 목록 페이지 스캔] ---
    def fetch_recipe_list(self, keyword, limit=10):
        """
        [흐름] 검색 키워드를 입력받아 상세 페이지로 이동할 수 있는 URL 리스트를 확보합니다.
        """
        list_driver = get_headless_driver()
        try:
            search_url = f"{self.base_url}/recipe/list.html?q={keyword}"
            list_driver.get(search_url)
            time.sleep(1.2) # 페이지 로딩 대기

            soup = BeautifulSoup(list_driver.page_source, 'html.parser')
            recipe_items = soup.select('#contents_area_full > ul > ul > li')
            
            titles, urls = [], []
            for item in recipe_items[:limit]: # 메모리 보호를 위해 limit 설정
                title_el = item.select_one('div.common_sp_caption_tit.line2')
                link_el = item.select_one('a.common_sp_link')
                
                if title_el and link_el:
                    titles.append(self.cleaner.clean_title(title_el.get_text()))
                    urls.append(self.base_url + link_el['href'])
            
            return titles, urls
        except Exception as e:
            print(f"❌ 목록 수집 중 오류: {e}")
            return [], []
        finally:
            list_driver.quit()

    # --- [내부 로직 2: 상세 페이지 정밀 수집] ---
    def fetch_detail_worker(self, title, url, category="일반"):
        """
        [흐름] 개별 레시피 페이지에 접속하여 재료와 조리법을 긁어오는 '일꾼'입니다.
        시니어 팁: 멀티스레딩을 위해 독립적인 함수로 설계했습니다.
        """
        worker_driver = get_headless_driver()
        try:
            worker_driver.get(url)
            time.sleep(1.0)
            soup = BeautifulSoup(worker_driver.page_source, 'html.parser')
            
            # 재료 추출
            material_tags = soup.select('#divConfirmedMaterialArea > ul:nth-child(1) > li')
            origin_mats = [self.cleaner.clean_material(m.get_text(separator=' ', strip=True)) for m in material_tags]
            
            # 조리 순서 추출
            step_list = soup.select('.view_step_cont')
            steps = [f"{i+1}. {self.cleaner.clean_title(s.get_text(strip=True))}" for i, s in enumerate(step_list)]

            # 딕셔너리 형태로 반환하여 나중에 DataFrame으로 합치기 쉽게 만듭니다.
            return {
                "title": title, 
                "url": url, 
                "category": category,
                "materials": origin_mats, 
                "steps": steps
            }
        except Exception as e:
            print(f"❌ 상세 수집 실패 [{title}]: {e}")
            return None
        finally:
            worker_driver.quit()

    # --- [핵심 모드 1: 카테고리별 초기 대량 수집] ---
    def collect_initial_batch(self):
        """
        [데이터 기획] 서비스 런칭 전, 배민 카테고리별로 데이터를 미리 비축합니다.
        """
        print("📦 [Batch Mode] 초기 카테고리 데이터 비축을 시작합니다...")
        for cat in CATEGORIES:
            print(f"📡 '{cat}' 카테고리 수집 중...")
            titles, urls = self.fetch_recipe_list(cat, limit=10) # 각 카테고리당 10개씩
            
            if not titles: continue

            # 병렬 수집 실행 (속도 향상)
            batch_data = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.fetch_detail_worker, titles[i], urls[i], cat) for i in range(len(urls))]
                for future in as_completed(futures):
                    res = future.result()
                    if res: batch_data.append(res)
            
            # 수집 즉시 DB 저장 (메모리 누수 방지)
            self._save_to_db(batch_data)
        print("✅ 모든 초기 데이터가 DB에 저장되었습니다.")

    # --- [핵심 모드 2: 실시간 온디맨드 수집] ---
    def collect_on_demand(self, keyword):
        """
        [서비스 로직] 사용자가 요청한 음식이 DB에 없을 때만 딱 하나를 정밀 수집합니다.
        """
        print(f"⚡ [On-demand Mode] '{keyword}' 실시간 수집 가동...")
        titles, urls = self.fetch_recipe_list(keyword, limit=1) # 가장 정확한 1개만 타겟팅
        
        if not titles: return None

        # 하나만 긁으므로 스레드 없이 가볍게 진행
        detail = self.fetch_detail_worker(titles[0], urls[0], category="실시간수집")
        
        if detail:
            # 챗봇이 바로 쓸 수 있도록 DataFrame으로 변환해서 반환
            manager = RecipeDataManager([detail])
            df = manager.process_to_dataframe()
            return df
        return None

    def _save_to_db(self, data_list):
        """
        [흐름] 리스트 데이터 전처리 -> 중복 검사 -> DB 최종 저장
        """
        if not data_list: 
            return
        
        # 1. [전처리] SQL 호환을 위해 리스트를 문자열로 변환
        for item in data_list:
            if isinstance(item.get('materials'), list):
                item['materials'] = ", ".join(item['materials'])
            if isinstance(item.get('steps'), list):
                item['steps'] = "\n".join(item['steps'])

        # 2. 데이터 프레임 생성
        manager = RecipeDataManager(data_list)
        df = manager.process_to_dataframe()
        
        if df is not None:
            try:
                conn = sqlite3.connect(self.db_path)
                
                # [시니어 팁: 중복 데이터 관리]
                # 이미 DB에 있는 제목(title)은 제외하고 새로운 것만 골라냅니다.
                try:
                    existing_titles = pd.read_sql("SELECT title FROM recipes", conn)['title'].tolist()
                    df = df[~df['title'].isin(existing_titles)] # 이미 있는 제목은 제외
                except:
                    # 테이블이 아예 없는 초기 단계라면 그냥 통과
                    pass

                if not df.empty:
                    # 3. 최종 저장 (중복 제거된 데이터만!)
                    df.to_sql('recipes', conn, if_exists='append', index=False)
                    print(f"💾 새로운 레시피 {len(df)}개가 지식 창고에 추가되었습니다.")
                else:
                    print("이미 모든 데이터가 DB에 존재하여 추가하지 않았습니다.")
                
                conn.close()
            except Exception as e:
                print(f"❌ DB 처리 중 오류 발생: {e}")    
            

# --- [메인 실행부] ---
if __name__ == "__main__":
    crawler = RecipeCrawler()
    # 1. 처음 실행할 때만 카테고리별로 데이터를 긁어옵니다. (주석 처리하며 관리 가능)
    crawler.collect_initial_batch()