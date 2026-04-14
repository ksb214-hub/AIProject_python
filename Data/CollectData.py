# 이 코드는 챗봇을 켜기 전, 혹은 정기적으로 데이터를 업데이트할 때 실행하는 **'공급망'**입니다.
import sqlite3
import pandas as pd

# [시니어 개발자의 데이터 기획 노트]
# 데이터 기획자는 '데이터의 영속성'을 고민해야 합니다. 
# 크롤링은 언제든 실패할 수 있지만, DB에 저장된 데이터는 우리 자산이 됩니다.

def update_recipe_database(processed_df):
    """
    [흐름: DataFrame -> SQLite DB 저장]
    가공된 데이터를 파일 형태의 DB인 SQLite에 저장합니다.
    """
    print("📦 데이터를 데이터베이스(DB)에 비축하는 중입니다...")
    
    # 1. DB 연결 (파일이 없으면 새로 생성됩니다)
    conn = sqlite3.connect('recipes.db')
    
    # 2. DataFrame을 SQL 테이블로 변환
    # if_exists='replace': 기존 데이터를 밀어내고 최신 데이터로 교체합니다.
    processed_df.to_sql('recipes', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ 데이터 비축 완료! 이제 챗봇이 이 데이터를 자유롭게 꺼내 쓸 수 있습니다.")

# (이 함수는 Crawling.py의 메인 로직 끝에서 호출하게 됩니다)

