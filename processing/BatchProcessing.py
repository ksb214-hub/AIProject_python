import sqlite3
import pandas as pd
from Data.DataCleaner import DataCleaner

def batch_clean_data():
    db_path = '/Users/gangseongbin/Desktop/develop/python/AIProject/recipes.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cleaner = DataCleaner()
    
    # [Step 0] 컬럼 추가 로직 (데이터를 가져오기 전에 먼저 수행)
    cursor.execute("PRAGMA table_info(recipes)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'pure_materials' not in columns:
        print("🔧 'pure_materials' 컬럼을 추가합니다...")
        cursor.execute("ALTER TABLE recipes ADD COLUMN pure_materials TEXT")
        conn.commit()
    else:
        print("✅ 이미 컬럼이 존재합니다.")

    # [Step 1] 데이터 불러오기
    df = pd.read_sql("SELECT * FROM recipes", conn)
    
    # [Step 2] 정제 로직 적용
    print(f"총 {len(df)}개의 레시피를 정제합니다...")
    print(df.columns) # 데이터프레임의 실제 컬럼명들을 확인
    df['pure_materials'] = df['materials'].apply(cleaner.clean_ingredient)
    
    # [Step 3] 데이터 업데이트 (executemany 사용으로 성능 최적화)
    # [수정] for 루프 대신 to_sql 사용
    print("🚀 정제된 데이터를 DB에 반영합니다...")
    
    # 'if_exists="replace"'는 테이블을 새로 갈아 끼우는 것이 아니라, 
    # 데이터를 갱신합니다. (이미 컬럼이 추가된 상태이므로 매우 안전합니다.)
    df.to_sql('recipes', conn, if_exists='replace', index=False)
        
    conn.commit()
    conn.close()
    print("✅ 모든 레시피 데이터 정제 완료!")

if __name__ == "__main__":
    batch_clean_data()