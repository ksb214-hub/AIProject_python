from bs4 import BeautifulSoup
from driver.driver_loader import get_headless_driver
from utils.data_processor import DataCleaner

class RecipeCrawler:
    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        self.driver = get_headless_driver() # 라이브러리 호출
        self.cleaner = DataCleaner()       # 가공 도구 로드

    def fetch_recipe_list(self, keyword):
        search_url = f"{self.base_url}/recipe/list.html?q={keyword}"
        self.driver.get(search_url)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # 레시피 개수 체크 (제공해주신 Selector 활용)
        count_tag = soup.select_one('#contents_area_full > ul > div > b')
        if not count_tag or count_tag.get_text().strip() == '0':
            return []

        # 레시피 카드 목록 추출
        items = soup.select('#contents_area_full > ul > ul > li')
        results = []

        for item in items:
            title_el = item.select_one('div.common_sp_caption_tit.line2')
            link_el = item.select_one('a.common_sp_link')

            if title_el and link_el:
                # 데이터 가공 라이브러리 사용
                clean_title = self.cleaner.clean_title(title_el.get_text())
                full_url = self.base_url + link_el['href']
                
                results.append({
                    "title": clean_title,
                    "url": full_url
                })
        
        return results

    def quit(self):
        self.driver.quit()

# 실행 테스트
if __name__ == "__main__":
    keyword = input("어떤 요리를 찾으시나요? : ")
    crawler = RecipeCrawler()
    
    try:
        data = crawler.fetch_recipe_list(keyword)
        for entry in data:
            print(f"제목: {entry['title']} | 링크: {entry['url']}")
    finally:
        crawler.quit()