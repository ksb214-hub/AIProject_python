import pandas as pd
import re
from Utils.ssl_helper import disable_ssl_verification

# SSL 인증 무시
disable_ssl_verification()

def get_meat_table(url="https://www.chabyulhwa.com/blog/dictionary34_pork"):
    """
    돼지고기 부위 데이터 테이블을 웹에서 가져와서 정제 후 DataFrame으로 반환
    """
    try:
        tables = pd.read_html(url)
        if not tables:
            print("테이블이 없습니다.")
            return None

        df = tables[0]

        # 가격 컬럼이 존재하면 숫자만 남기기
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
        df.to_csv("data/meat_parts.csv", index=False)