# Crawling/Crawling.py
# 이 파일은 프로젝트의 **'컨트롤러'**입니다. 
# 위 라이브러리들을 사용하여 실제로 웹사이트에 접속하고 데이터를 리스트화합니다.

import time
from bs4 import BeautifulSoup
# [흐름: 상위 패키지로부터 드라이버 및 가공 도구 임포트]
from driver.driver_loader import get_headless_driver
from utils.data_processor import DataCleaner

class RecipeCrawler:
    """
    [전체 흐름: 검색 -> 검증 -> 순회 -> 저장]
    만개의레시피 사이트에서 목록 데이터를 수집하는 메인 클래스
    """
    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        # 초기화 시 드라이버 셋팅 라이브러리 호출
        self.driver = get_headless_driver()
        # 데이터 가공용 라이브러리 인스턴스 생성
        self.cleaner = DataCleaner()

    def fetch_recipe_list(self):
        # [단계 1] 사용자 입력 받기
        keyword = input("어떤 레시피를 검색할까요? : ")
        
        # [단계 2] 검색 URL 접속
        search_url = f"{self.base_url}/recipe/list.html?q={keyword}"
        self.driver.get(search_url)
        time.sleep(1) # 페이지 렌더링 완료를 위한 대기시간

        # [단계 3] HTML 파싱 (BeautifulSoup 연동)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # [단계 4] 검색 결과 유무 확인
        # Selector를 통해 레시피 개수 텍스트 추출
        count_tag = soup.select_one('#contents_area_full > ul > div > b')
        
        # 결과가 없거나 0이면 즉시 종료 (Early Exit 패턴)
        if not count_tag or count_tag.get_text().strip() == '0':
            print(f"'{keyword}'에 대한 검색 결과가 없습니다.")
            return [], []

        # [단계 5] 레시피 목록 요소 추출
        recipe_items = soup.select('#contents_area_full > ul > ul > li')

        titles = [] # 제목 저장 리스트
        urls = []   # 상세 주소 저장 리스트

        # [단계 6] 각 카드 요소별 순회 및 데이터 추출
        for item in recipe_items:
            # 제목이 들어있는 태그와 상세 링크가 들어있는 태그 선택
            title_el = item.select_one('div.common_sp_caption_tit.line2')
            link_el = item.select_one('a.common_sp_link')

            if title_el and link_el:
                # [데이터 가공] 라이브러리를 사용하여 제목 정제
                clean_title = self.cleaner.clean_title(title_el.get_text())
                
                # [상세 주소 조합] 상대 경로(/recipe/123)를 절대 경로(http://...)로 변환
                full_url = self.base_url + link_el['href']

                titles.append(clean_title)
                urls.append(full_url)

        return titles, urls

    def close(self):
        """드라이버 및 브라우저 프로세스 안전 종료"""
        if self.driver:
            self.driver.quit()

# [메인 실행부]
if __name__ == "__main__":
    crawler = RecipeCrawler()
    try:
        # 크롤링 시작
        titles, urls = crawler.fetch_recipe_list()
        
        # 결과 출력 (데이터 정합성 확인)
        for i, (t, u) in enumerate(zip(titles, urls), 1):
            print(f"[{i}] {t} \n    링크: {u}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 오류 발생 여부와 상관없이 반드시 드라이버 종료
        crawler.close()