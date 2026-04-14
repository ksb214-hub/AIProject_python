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
        [흐름: 수집 데이터 로드 -> 문자열 병합(Join) -> 중복 URL 제거 -> 최종 반환]
        """
        if not self.raw_data: 
            print("⚠️ 가공할 데이터가 비어있습니다.")
            return None

        # 1. 원본 리스트를 데이터프레임으로 변환
        df = pd.DataFrame(self.raw_data)

        # 2. [핵심 가공] SQLite 호환 및 챗봇 응답용 텍스트 생성
        # 리스트 형태의 원본 데이터를 문자열로 변환하여 새로운 컬럼에 저장하거나 덮어씌웁니다.
        
        # 원본 재료 (예: ["감자 1개", "양파 1/2개"]) -> "감자 1개, 양파 1/2개"
        if 'materials' in df.columns:
            df['materials'] = df['materials'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
            
        # 정제된 재료 (예: ["감자", "양파"]) -> "감자, 양파"
        if 'pure_materials' in df.columns:
            df['pure_materials_str'] = df['pure_materials'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
            
        # 조리 단계 (예: ["1. 씻기", "2. 볶기"]) -> "1. 씻기\n2. 볶기"
        if 'steps' in df.columns:
            df['steps'] = df['steps'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)

        # 3. [데이터 무결성] 동일한 레시피(URL 기준) 중복 제거
        df.drop_duplicates(subset=['url'], keep='first', inplace=True)
        
        # 4. [인덱스 초기화] 중복 제거 후 번호를 다시 매깁니다.
        df.reset_index(drop=True, inplace=True)
        
        print(f"✅ 데이터 가공 완료: {len(df)}건의 유니크 레시피 확보")
        return df