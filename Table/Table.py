# 웹페이지 접속
# ↓
# HTML Table 수집
# ↓
# 가격 데이터 정제
# ↓
# DataFrame 생성
# ↓
# 그래프 시각화

import pandas as pd
import matplotlib.pyplot as plt
import re
from Utils.ssl_helper import disable_ssl_verification

# SSL 인증 무시
disable_ssl_verification()
# 크롤링 대상 URL (고정)
URL = "https://www.martjob.co.kr/news/foodlist.asp"


def get_table_data():
    """
    웹페이지에서 HTML Table 데이터 가져오기
    """

    print("웹 페이지에서 식자재 가격 데이터를 수집 중...")

    tables = pd.read_html(URL)

    if len(tables) == 0:
        print("Table 데이터를 찾을 수 없습니다.")
        return None

    df = tables[0]

    return df


def clean_price(price):
    """
    가격 문자열 정제
    예: 12,000원 → 12000
    """

    price = str(price)

    price = re.sub("[^0-9]", "", price)

    if price == "":
        return 0

    return int(price)


def preprocess_data(df):
    """
    DataFrame 정제
    """

    print("데이터 정제 중...")

    # 컬럼 이름 정리 (사이트 구조에 따라 변경 가능)
    df = df.iloc[:, :2]

    df.columns = ["재료", "가격"]

    df["가격"] = df["가격"].apply(clean_price)

    return df


def visualize_data(df):
    """
    가격 데이터 그래프 생성
    """

    print("그래프 생성 중...")

    plt.figure(figsize=(10, 5))

    plt.bar(df["재료"], df["가격"])

    plt.title("식자재 가격 비교")
    plt.xlabel("재료")
    plt.ylabel("가격")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


def main():

    # 1 Table 수집
    df = get_table_data()

    if df is None:
        return

    # 2 데이터 정제
    df = preprocess_data(df)

    # 3 데이터 출력
    print("\n식자재 가격 데이터")
    print(df)

    # 4 그래프 출력
    visualize_data(df)


if __name__ == "__main__":
    main()