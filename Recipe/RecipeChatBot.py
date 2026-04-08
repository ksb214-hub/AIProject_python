import pandas as pd
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# [시니어 개발자의 설계 노트]
# 1. 데이터 로드: 크롤링된 DataFrame을 챗봇이 읽을 수 있는 지식원으로 활용합니다.
# 2. 학습(Training): 레시피 제목을 기반으로 질문-답변 쌍을 생성하여 학습시킵니다.
# 3. 로직 분기: 사용자의 의도(재료 궁금함 vs 조리법 궁금함)를 파악하여 답변합니다.

class RecipeAssistant:
    def __init__(self, recipe_df):
        """
        [흐름: 챗봇 초기화 및 지식 베이스(DataFrame) 연결]
        """
        self.db = recipe_df
        # 챗봇 객체 생성 (데이터 보관 및 논리 처리를 담당)
        self.bot = ChatBot(
            'RecipeMaster',
            logic_adapters=[
                'chatterbot.logic.BestMatch', # 가장 유사한 질문을 찾는 로직
                'chatterbot.logic.MathematicalEvaluation' # 수치 계산 필요 시 사용
            ]
        )
        self.trainer = ListTrainer(self.bot)

    def train_with_recipes(self):
        """
        [흐름: 크롤링 데이터 -> 대화형 리스트 변환 -> 학습]
        - 레시피 제목을 학습시켜 사용자가 제목만 말해도 대응하게 합니다.
        """
        print("🤖 레시피 데이터를 기반으로 인공지능 학습을 시작합니다...")
        
        for _, row in self.db.iterrows():
            # 대화 패턴 학습: "제목 알려줘" -> "해당 레시피는 ~입니다"
            conversation = [
                row['title'],
                f"{row['title']} 레시피를 찾으셨군요! 재료가 궁금하신가요, 아니면 조리 순서가 궁금하신가요?"
            ]
            self.trainer.train(conversation)
        print("✅ 학습이 완료되었습니다.")

    def get_recipe_info(self, user_input):
        """
        [흐름: 사용자 입력 분석 -> 데이터 검색 -> 맞춤 답변 추출]
        """
        # 1. 사용자가 언급한 레시피 제목이 데이터에 있는지 확인 (키워드 매칭)
        # 10년차 노하우: 완전 일치가 아닌 '포함' 여부로 유연하게 검색합니다.
        matched_recipe = self.db[self.df_contains(user_input)]

        if not matched_recipe.empty:
            recipe = matched_recipe.iloc[0]
            
            # 2. 사용자의 의도 파악 (재료 vs 순서)
            if '재료' in user_input or '뭐 들어가' in user_input:
                return f"📍 [{recipe['title']}]의 재료입니다:\n{recipe['materials_str']}"
            
            elif '순서' in user_input or '방법' in user_input or '어떻게' in user_input:
                return f"👨‍🍳 [{recipe['title']}] 조리 순서입니다:\n{recipe['steps_display']}"
            
            else:
                return f"<{recipe['title']}> 레시피가 준비되어 있습니다. '재료'나 '조리 순서'를 물어봐 주세요!"

        # 3. 데이터에 없는 경우 ChatterBot의 기본 응답 엔진 사용
        return self.bot.get_response(user_input)

    def df_contains(self, user_input):
        """제목 포함 여부를 체크하는 헬퍼 함수"""
        return self.db['title'].apply(lambda x: x in user_input or user_input in x)

# --- [Main Execution Flow] ---
def run_recipe_chatbot(processed_df):
    """
    [전체 실행 흐름]
    1. 가공된 데이터를 챗봇 엔진에 주입합니다.
    2. 데이터셋의 모든 레시피 제목을 학습시킵니다.
    3. 무한 루프를 통해 사용자와 대화를 주고받습니다.
    """
    # 챗봇 인스턴스 생성
    assistant = RecipeAssistant(processed_df)
    
    # 레시피 학습 (크롤링한 40개 데이터 주입)
    assistant.train_with_recipes()

    print("\n" + "="*50)
    print("🥘 AI 레시피 가이드 대화를 시작합니다! (종료: '종료')")
    print("예시: '목살스테이크 재료 알려줘', '돼지고기 김치찌개 조리법 뭐야?'")
    print("="*50)

    while True:
        user_msg = input("\n나: ")
        if user_msg in ['종료', 'exit', 'quit']:
            print("🤖 즐거운 요리 시간 되세요! 종료합니다.")
            break

        # 챗봇의 핵심 로직 호출
        response = assistant.get_recipe_info(user_msg)
        print(f"🤖 챗봇: {response}")

# 이 코드는 Crawling.py의 메인 섹션 하단에서 호출됩니다.
# run_recipe_chatbot(processed_df)