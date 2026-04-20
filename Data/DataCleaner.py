import re
from konlpy.tag import Okt

class DataCleaner:
    def __init__(self):
        self.okt = Okt()
        # 재료 사전: 부위와 재료를 매칭하여 관리
        # 이제는 '치환'하지 않고, 어떤 재료가 어떤 카테고리에 속하는지만 정의합니다.
        self.ingredient_categories = {
            '소고기': ['불고기감', '한우', '다짐육', '양지', '사태', '등심', '안심'],
            '양파': ['자색양파', '양파즙'],
            '돼지고기': ['삼겹살', '목살', '뒷다리살', '앞다리살', '항정살']
        }

    def clean_ingredient(self, raw_text):
        # [Step 1] 숫자 및 단위 제거
        clean_text = re.sub(r'[0-9]+[가-힣a-zA-Z]*', '', raw_text)
        
        # [Step 2] 형태소 분석기로 명사 추출
        nouns = self.okt.nouns(clean_text)
        
        final_result = []
        for noun in nouns:
            if len(noun) < 2: continue # 1글자 단어는 노이즈일 확률이 높아 제외
            
            # [Step 3] 부위명과 재료명 보존 및 매칭
            # 1. 만약 사전에 있는 '부위'라면, 그 부위와 상위 재료를 모두 추가
            is_matched = False
            for category, parts in self.ingredient_categories.items():
                if noun == category or noun in parts:
                    final_result.append(category) # 상위 재료 추가
                    final_result.append(noun)     # 구체적인 부위 추가
                    is_matched = True
                    break
            
            # 2. 사전에 없는 새로운 재료라면 그대로 추가
            if not is_matched:
                final_result.append(noun)
        
        # 중복 제거 (소고기, 양지, 소고기 -> 소고기, 양지)
        return ", ".join(list(set(final_result)))

# --- 실행 테스트 ---
if __name__ == "__main__":
    cleaner = DataCleaner()
    print(f"결과: {cleaner.clean_ingredient('양지 소고기 500g, 삼겹살 2줄')}")
    # 출력값: "소고기, 삼겹살, 양지, 돼지고기"