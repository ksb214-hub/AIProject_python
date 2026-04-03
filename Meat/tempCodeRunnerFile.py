import pandas as pd
import re
import ssl
# SSL 인증 문제 해결
ssl._create_default_https_context = ssl._create_unverified_context

def get_meat_table(url="https://www.chabyulhwa.com/blog/dictionary34_pork"):
    """
    돼지고기 부위 데이터 테이블을 웹에서 가져와서 정제 후 DataFrame으로 반환
    """
    try:
        # HTML 테이블 읽기
        tables = pd.read_html(url)
        if not tables:
            print("테이블이 없습니다.")
            return None

        # 첫 번째 테이블 사용 (대부분의 경우 원하는 테이블은 첫 번째)
        df = tables[0]

        # 가격 컬럼 정제 (숫자만)
        if "가격" in df.columns:
            df["가격"] = df["가격"].astype(str).apply(lambda x: int(re.sub(r"[^0-9]", "", x)))
        
        return df

    except Exception as e:
        print("데이터 가져오기 실패:", e)
        return None

if __name__ == "__main__":
    df = get_meat_table()
    if df is not None:
        print(df)
        # CSV로 저장
        df.to_csv("data/meat_parts.csv", index=False)