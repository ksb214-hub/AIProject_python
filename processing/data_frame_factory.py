# 데이터 가공 라이브러리 (processing/data_frame_factory.py)
# 이 모듈은 수집된 dict 형태의 리스트를 받아서 정형화된 DataFrame으로 변환하고 저장하는 역할을 합니다.

import pandas as pd

class RecipeDataManager:
    """
    [데이터 검증 레이어]
    수집된 raw_data를 DataFrame으로 변환하고, 저장 전 상태를 모니터링합니다.
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.df = None

    def process_to_dataframe(self):
        """
        [흐름: 변환 -> 정제 -> 검증 출력]
        """
        if not self.raw_data:
            print("\n[⚠️ Alert] 전달된 데이터가 없어 DataFrame을 생성할 수 없습니다.")
            return None

        # 1. 변환
        self.df = pd.DataFrame(self.raw_data)

        # 2. 가공 (재료 리스트를 문자열로 결합)
        self.df['materials_str'] = self.df['materials'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else ""
        )

        # 3. 데이터 중복 제거
        self.df.drop_duplicates(subset=['url'], keep='first', inplace=True)

        # [검증 단계] 출력 섹션
        print("\n" + "="*50)
        print("📊 DATAFRAME 가공 결과 보고서")
        print("="*50)
        
        # 데이터 크기 확인
        print(f"1. 전체 행/열 크기: {self.df.shape} (행, 열)")
        
        # 컬럼명 및 데이터 타입 확인
        print("\n2. 컬럼 정보:")
        print(self.df.dtypes)
        
        # 데이터 샘플 확인 (상위 5개)
        print("\n3. 데이터 샘플 (상단 5개):")
        # 모든 컬럼이 잘 보이도록 옵션 설정 (선택 사항)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.df.head(5))
        
        print("="*50 + "\n")
        
        return self.df