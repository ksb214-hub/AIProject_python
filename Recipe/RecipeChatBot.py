import sqlite3
import pandas as pd
from Crawling.Crawling import RecipeCrawler 
from recommend.Recommend import AIRecipeRecommender

class RecipeAssistant:
    def __init__(self):
        self.db_path = 'recipes.db'
        self.crawler = RecipeCrawler()
        self.recommender = AIRecipeRecommender(self.db_path)
        
        # DB 스키마 자동 업데이트
        self._upgrade_schema()
        
        self.user_persona = None  
        self.current_recipe = None  # 현재 대화 중인 레시피 (상태 저장)
        self.last_recommendations = None

    def _upgrade_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(recipes)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'persona_tag' not in columns:
                cursor.execute("ALTER TABLE recipes ADD COLUMN persona_tag TEXT")
                conn.commit()
        finally:
            conn.close()

    def get_response(self, user_input):
        clean_input = user_input.replace(" ", "")

        # --- [Step 1: 페르소나 설정] ---
        persona_msg = self._check_and_set_persona(clean_input)
        if persona_msg:
            return persona_msg

        # --- [Step 2: 긍정 응답 및 맥락 처리 (핵심 수정)] ---
        # AI가 방금 제안한 레시피가 있고, 사용자가 긍정적인 답변을 했을 때
        confirm_words = ['응', '어', '안내해줘', '알려줘', '보여줘', '좋아', '그래', '안내해', '레시피제공해줘']
        if self.current_recipe is not None and any(w in clean_input for w in confirm_words):
            recipe = self.current_recipe
            self.current_recipe = None # 출력 후 상태 초기화
            return (f"📝 요청하신 <{recipe['title']}> 상세 정보입니다!\n\n"
                    f"📍 [재료]: {recipe['materials']}\n"
                    f"🔗 [링크]: {recipe['url']}\n\n"
                    f"도움이 되셨나요? 다른 요리도 물어봐 주세요!")

        # --- [Step 3: 검색 로그 기록 (AI 학습용)] ---
        self.recommender.log_search(user_input)

        # --- [Step 4: AI 추천 로직 (뭐 먹지/추천 키워드)] ---
        if any(word in clean_input for word in ['추천', '뭐먹지', '메뉴추천']):
            recommendations = self.recommender.get_ai_recommendations(limit=3)
            if recommendations is not None and not recommendations.empty:
                self.last_recommendations = recommendations
                msg = f"✨ {self.user_persona or '사용자'}님 취향 분석 결과입니다!\n"
                for i, row in recommendations.iterrows():
                    msg += f"📍 {row['title']} (유사도: {row.get('similarity_score', 0):.2f})\n"
                msg += "\n이 중 상세 정보가 궁금한 메뉴가 있으신가요?"
                return msg

        # --- [Step 5: DB 내 레시피 직접 검색] ---
        # 사용자가 메뉴 이름을 직접 말했을 경우
        recipe = self._search_db_with_persona(user_input)
        if recipe is not None:
            self.current_recipe = recipe # 찾은 레시피를 상태에 저장
            return f"✅ DB에서 찾았습니다! <{recipe['title']}> 레시피의 상세 내용을 알려드릴까요?"

        # --- [Step 6: 실시간 수집 (진짜 없을 때만)] ---
        if len(clean_input) > 1:
            print(f"🔍 DB에 정보가 없어 실시간 수집을 시도합니다: {user_input}")
            new_data_df = self.crawler.collect_on_demand(user_input)
            
            if new_data_df is not None and not new_data_df.empty:
                self.current_recipe = new_data_df.iloc[0] # 수집된 레시피 저장
                # 데이터 비축 시 페르소나 태그 추가
                new_data_df['persona_tag'] = self.user_persona
                self._save_to_db(new_data_df)
                return f"🔍 새로 찾아왔어요! <{self.current_recipe['title']}> 레시피입니다. 안내해 드릴까요?"

        return "어떤 요리가 궁금하신가요? '자취생'이라고 말씀하시면 맞춤 추천이 가능합니다!"

    def _check_and_set_persona(self, clean_input):
        if '자취' in clean_input:
            self.user_persona = '자취생'
            return "🏠 [자취생 모드 활성] 간단하고 가성비 좋은 요리 위주로 추천할게요!"
        if '초보' in clean_input or '요린이' in clean_input:
            self.user_persona = '요리 초보'
            return "🐣 [요리 초보 모드 활성] 실패 없는 황금 레시피 위주로 찾아드릴게요!"
        return None

    def _search_db_with_persona(self, keyword):
        conn = sqlite3.connect(self.db_path)
        # 검색어가 제목에 포함되어 있는지 확인
        query = "SELECT * FROM recipes WHERE title LIKE ?"
        params = [f'%{keyword}%']
        
        # 페르소나 가중치 (옵션)
        if self.user_persona == '자취생':
            query += " AND (title LIKE '%간단%' OR title LIKE '%전자레인지%' OR title LIKE '%자취%')"
        
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df.iloc[0] if not df.empty else None

    def _save_to_db(self, df):
        conn = sqlite3.connect(self.db_path)
        df.to_sql('recipes', conn, if_exists='append', index=False)
        conn.close()

# --- 실행 메인 루프 ---
if __name__ == "__main__":
    assistant = RecipeAssistant()
    print("==========================================")
    print("📢 요리 보조 AI 챗봇 서비스를 시작합니다!")
    print("   (종료하시려면 '종료', 'exit', 'q'를 입력하세요)")
    print("==========================================")

    while True:
        user_input = input("\n👤 **님: ")
        if user_input.lower() in ['종료', 'exit', 'q', 'quit', '끝']:
            print("\n🤖 챗봇: 즐거운 요리 시간 되세요! 프로그램을 종료합니다.")
            break
        response = assistant.get_response(user_input)
        print(f"🤖 챗봇: {response}")