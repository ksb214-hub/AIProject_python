# 데이터 가공 라이브러리 (processing/data_frame_factory.py)
# 이 모듈은 수집된 dict 형태의 리스트를 받아서 정형화된 DataFrame으로 변환하고 저장하는 역할을 합니다.

import pandas as pd

class RecipeDataManager:
    """
    [Data Flow: List[Dict] -> DataFrame -> 필드 최적화 -> 최종 데이터셋]
    1. 여러 스레드에서 수집된 개별 레시피 딕셔너리들을 하나의 거대한 표로 통합합니다.
    2. 서비스(챗봇)에서 즉시 출력할 수 있도록 리스트를 문자열(String)로 직렬화합니다.
    """
    def __init__(self, raw_data):
        self.raw_data = raw_data


    def process_to_dataframe(self):
        """
        [흐름: 수집 데이터 로드 -> 문자열 병합(Join) -> 중복 URL 제거 -> 리포트 생성]
        """
        if not self.raw_data: return None

        df = pd.DataFrame(self.raw_data)

        # [데이터 가공 흐름] 챗봇 응답용 텍스트 생성
        # 리스트 형태의 재료/단계를 사람이 읽기 편한 줄바꿈/콤마 텍스트로 변환합니다.
        if 'materials' in df.columns:
            df['materials_str'] = df['materials'].apply(lambda x: ', '.join(x) if isinstance(x, list) else "")
        # --- 🔎 이 부분이 누락되어 에러가 발생했습니다! 추가해 주세요 ---
        if 'pure_materials' in df.columns:
            df['pure_materials_str'] = df['pure_materials'].apply(lambda x: ', '.join(x) if isinstance(x, list) else "")
        if 'steps' in df.columns:
            df['steps_display'] = df['steps'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else "")

        # [데이터 무결성 흐름] 동일한 레시피가 중복 저장되지 않도록 URL을 기준으로 고유값만 남깁니다.
        df.drop_duplicates(subset=['url'], keep='first', inplace=True)
        
        return df