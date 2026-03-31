import pandas as pd
import os
from Crawling.Crawling import crawl

def run_scheduler():

    search_keywords = ["김치", "돼지고기", "닭", "간단요리"]

    all_df = []

    for keyword in search_keywords:
        print(f"수집 중: {keyword}")
        df = crawl(keyword, limit=5)
        all_df.append(df)

    final_df = pd.concat(all_df, ignore_index=True)

    # 기존 파일 있으면 이어쓰기
    file_path = "data/recipes.csv"

    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        final_df = pd.concat([old_df, final_df], ignore_index=True)

    # 저장
    final_df.to_csv(file_path, index=False, encoding="utf-8-sig")

    print("자동 수집 완료")