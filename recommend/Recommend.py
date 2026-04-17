import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AIRecipeRecommender:
    """
    [Sprint 2] AI 기반 추천 엔진
    사용자의 최근 검색어 5개를 분석하여 전체 DB 레시피 중 가장 유사한 5개를 추천합니다.
    """
    def __init__(self, db_path='recipes.db'):
        # 현재 파일 위치 기준이 아니라 프로젝트 루트 기준으로 DB 경로를 잡는 것이 안전합니다.
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """검색 기록을 저장할 테이블이 없으면 생성"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # IF NOT EXISTS를 통해 테이블이 없을 때만 생성합니다.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            print("✅ DB 초기화 완료: search_history 테이블 준비됨")
        except Exception as e:
            print(f"❌ DB 초기화 실패: {e}")
            
    def _get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def log_search(self, keyword):
        """사용자의 검색 활동 기록 (챗봇이 호출)"""
        if not keyword: return
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO search_history (keyword) VALUES (?)", (keyword.strip(),))
        conn.commit()
        conn.close()

    def get_ai_recommendations(self, limit=5):
        """
        [핵심 로직]
        1. 최근 검색어 5개 로드
        2. 전체 레시피 데이터(제목+재료) 로드
        3. TF-IDF 벡터화 및 코사인 유사도 계산
        """
        conn = self._get_db_connection()
        
        try:
            # 1. 사용자 최근 검색어 5개 가져오기
            history_df = pd.read_sql(
                "SELECT keyword FROM search_history ORDER BY created_at DESC LIMIT 5", conn
            )
            
            # 2. 전체 레시피 로드 (가공된 문자열 컬럼 사용)
            recipes_df = pd.read_sql("SELECT * FROM recipes", conn)

            if history_df.empty or recipes_df.empty:
                print("💡 데이터가 부족하여 기본 추천(랜덤)을 수행합니다.")
                return pd.read_sql("SELECT * FROM recipes ORDER BY RANDOM() LIMIT ?", conn, params=(limit,))

            # 3. 텍스트 데이터 전처리
            # 사용자의 최근 관심사를 하나의 문장으로 합침 (예: "김치찌개 삼겹살 고추장 돼지고기 찌개")
            user_interest_profile = " ".join(history_df['keyword'].tolist())
            
            # 레시피의 '특징' 생성 (제목과 재료 정보를 합쳐서 분석의 깊이를 더함)
            recipes_df['feature_text'] = recipes_df['title'] + " " + recipes_df['materials']
            
            # 4. TF-IDF 벡터화 학습
            # stop_words를 조절하여 분석 품질을 높일 수 있습니다.
            tfidf = TfidfVectorizer()
            # 전체 레시피 특징들로 학습
            tfidf_matrix = tfidf.fit_transform(recipes_df['feature_text'])
            
            # 사용자 관심사를 동일한 벡터 공간으로 변환
            user_vector = tfidf.transform([user_interest_profile])

            # 5. 코사인 유사도 계산 (사용자 취향 vs 모든 레시피)
            # 결과값은 0~1 사이이며, 1에 가까울수록 유사함
            cosine_sim = cosine_similarity(user_vector, tfidf_matrix).flatten()

            # 6. 유사도 점수 기반 정렬 및 상위 인덱스 추출
            # argsort()는 오름차순이므로 [::-1]로 뒤집어 내림차순 정렬
            related_indices = cosine_sim.argsort()[::-1][:limit]
            
            # 추천 결과에 유사도 점수 추가 (디버깅 및 시각화용)
            recommendations = recipes_df.iloc[related_indices].copy()
            recommendations['similarity_score'] = cosine_sim[related_indices]

            print(f"✅ AI 분석 완료: '{user_interest_profile}' 기반 추천 생성")
            return recommendations

        except Exception as e:
            print(f"❌ AI 추천 생성 오류: {e}")
            return None
        finally:
            conn.close()

# --- 실행 테스트 (Sprint 2 검증) ---
if __name__ == "__main__":
    recommender = AIRecipeRecommender()
    
    # 챗봇이 사용자의 발화를 5번 기록했다고 가정
    test_keywords = ["돼지고기", "고추장", "매운 요리", "제육볶음", "자취생 반찬"]
    for k in test_keywords:
        recommender.log_search(k)
        
    # AI 추천 실행
    results = recommender.get_ai_recommendations(limit=5)
    
    if results is not None:
        print("\n🤖 AI 챗봇의 맞춤 레시피 추천:")
        for i, row in results.iterrows():
            print(f"[{i}] {row['title']} (유사도: {row['similarity_score']:.2f})")
            print(f"   ㄴ 재료: {row['materials'][:50]}...")