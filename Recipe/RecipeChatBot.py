import sqlite3
import pandas as pd
from Crawling.Crawling import RecipeCrawler 

class RecipeAssistant:
    def __init__(self):
        """
        [시니어의 설계 의도]
        1. self.user_persona: 사용자의 성향을 저장하여 맞춤형 필터링을 수행합니다.
        2. self.crawler: DB에 데이터가 없을 때만 깨어나는 정예 요원입니다.
        """
        self.db_path = 'recipes.db'
        self.crawler = RecipeCrawler()
        self.user_persona = None  # 사용자 페르소나 (자취생/요리 초보 등)
        self.current_recipe = None

    def get_response(self, user_input):
        """
        [흐름: 페르소나 설정 체크 -> DB 검색(페르소나 반영) -> 실시간 수집 -> 답변]
        """
        clean_input = user_input.replace(" ", "")

        # --- [Step 1: 페르소나 설정/변경 로직] ---
        # 사용자가 본인의 상태를 말하면 페르소나를 고정합니다.
        persona_msg = self._check_and_set_persona(clean_input)
        if persona_msg:
            return persona_msg

        # --- [Step 2: DB 검색 (페르소나 필터링 포함)] ---
        # 데이터 기획자라면 여기서 페르소나에 맞는 키워드를 쿼리에 섞어야 합니다.
        recipe = self._search_db_with_persona(clean_input)
        
        if recipe is not None:
            self.current_recipe = recipe
            return f"✅ {self.user_persona or '사용자'}님께 딱 맞는 레시피를 DB에서 찾았습니다!\n<{recipe['title']}>입니다. 재료나 순서를 알려드릴까요?"

        # --- [Step 3: 온디맨드 실시간 수집] ---
        # DB에 없을 때만 실행하여 리소스를 아낍니다.
        if any(word in clean_input for word in ['알려줘', '찾아줘', '방법', '레시피']):
            print(f"🔍 '{user_input}' 정보가 없어 실시간 수집 및 페르소나 매칭을 시작합니다...")
            new_data_df = self.crawler.collect_on_demand(user_input)
            
            if new_data_df is not None and not new_data_df.empty:
                # 수집된 데이터에 현재 페르소나 태그를 입혀서 저장 (데이터 자산화)
                new_data_df['persona_tag'] = self.user_persona
                self._save_to_db(new_data_df)
                
                self.current_recipe = new_data_df.iloc[0]
                return f"✨ 실시간으로 찾아왔어요! <{self.current_recipe['title']}> 레시피를 안내해 드릴게요."

        return "어떤 요리가 궁금하신가요? '자취생'이나 '요리 초보'라고 말씀하시면 맞춤 추천도 가능해요!"

    def _check_and_set_persona(self, clean_input):
        """사용자의 입력을 감지해 페르소나를 설정하는 내부 로직"""
        if '자취' in clean_input or '혼자' in clean_input:
            self.user_persona = '자취생'
            return "🏠 [자취생 모드 활성] 간단하고 가성비 좋은 요리 위주로 보여드릴게요!"
        if '초보' in clean_input or '요린이' in clean_input:
            self.user_persona = '요리 초보'
            return "🐣 [요리 초보 모드 활성] 실패 없는 황금 레시피 위주로 찾아드릴게요!"
        return None

    def _search_db_with_persona(self, keyword):
        """
        [데이터 기획의 핵심] 
        사용자 페르소나에 따라 SQL 쿼리에 가중치를 둡니다.
        """
        conn = sqlite3.connect(self.db_path)
        
        # 기본 쿼리: 제목 검색
        query = f"SELECT * FROM recipes WHERE title LIKE '%{keyword}%'"
        
        # 페르소나가 설정되어 있다면 해당 태그가 있는 데이터를 우선적으로 가져오도록 기획 가능
        # (여기서는 간단하게 제목에 페르소나 관련 키워드가 있는지도 함께 검색)
        if self.user_persona == '자취생':
            query += " AND (title LIKE '%간단%' OR title LIKE '%한그릇%' OR title LIKE '%전자레인지%')"
        elif self.user_persona == '요리 초보':
            query += " AND (title LIKE '%황금%' OR title LIKE '%백종원%' OR title LIKE '%비법%')"

        df = pd.read_sql(query, conn)
        conn.close()
        return df.iloc[0] if not df.empty else None

    def _save_to_db(self, df):
        """새 데이터를 DB에 추가 (메모리 절약 및 데이터 비축)"""
        conn = sqlite3.connect(self.db_path)
        df.to_sql('recipes', conn, if_exists='append', index=False)
        conn.close()