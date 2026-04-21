import sqlite3
import pandas as pd
import re
from konlpy.tag import Okt

# 1. 완전 정제 클래스 재정의
class DataCleaner:
    def __init__(self):
        self.ingredient_map = {
            '소고기': ['소고기', '불고기감', '한우', '다짐육', '양지', '사태', '등심', '안심', '국거리', '불고기'],
            '양념': ['간장', '설탕', '참기름', '소금', '후추', '고추장', '올리고당', '식초', '마요네즈', '버터', '후춧가루', '겨자', '올리브유'],
            '채소': ['양파', '자색양파', '대파', '마늘', '청양고추', '당근', '애호박', '감자', '느타리버섯', '옥수수', '파슬리', '표고버섯', '피망', '고추'],
            '기타': ['달걀', '계란', '두부', '다시마', '멸치', '우유', '치즈', '식용유', '당면', '오징어', '고등어']
        }
        # 모든 허용 가능한 단어를 하나의 집합으로 만듭니다.
        self.all_keywords = {word for sublist in self.ingredient_map.values() for word in sublist}

    def clean_ingredient(self, raw_text):
        if not raw_text: return ""
        
        results = set()
        # raw_text에서 우리가 아는 재료들만 찾아냅니다.
        for category, parts in self.ingredient_map.items():
            for part in parts:
                if part in raw_text:
                    results.add(f"{category}:{part}")
        
        return ", ".join(sorted(list(results)))
# 2. DB 완전 초기화 및 갱신
db_path = "/Users/gangseongbin/Desktop/develop/python/AIProject/recipes.db"
conn = sqlite3.connect(db_path)
cleaner = DataCleaner()

# 원본 'materials' 컬럼만 읽어옴
df = pd.read_sql("SELECT materials FROM recipes", conn)
# 완전 재정제
df['pure_materials'] = df['materials'].apply(cleaner.clean_ingredient)

# 덮어쓰기
df.to_sql('recipes', conn, if_exists='replace', index=False)
conn.close()
print("✅ DB가 원본 기반으로 완전히 새로 정제되었습니다.")