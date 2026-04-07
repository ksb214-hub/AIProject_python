# utils/data_processor.py
# 이 파일은 수집된 가공되지 않은 데이터를 **'정제'**하는 곳입니다. 
# 챗봇이 자연스럽게 말할 수 있도록 텍스트의 불순물을 제거합니다.

import re

class DataCleaner:
    """
    [흐름: 원본 텍스트 입력 -> 정규표현식 필터링 -> 정제된 텍스트 반환]
    데이터의 일관성을 유지하기 위한 가공 유틸리티 클래스
    """
    
    @staticmethod
    def clean_title(title_text):
        """
        레시피 제목에 포함된 특수문자나 불필요한 줄바꿈 제거
        """
        if not title_text: 
            return ""
        
        # 1. \n, \r, \t 등 제어 문자를 공백으로 치환
        # 2. re.sub(r'\s+', ' ', ...) : 연속된 공백을 하나로 합침
        refined = re.sub(r'\s+', ' ', title_text).strip()
        
        # 3. 추가적인 특수 기호 정제가 필요할 경우 여기에 패턴 추가 가능
        return refined

    @staticmethod
    def extract_id_from_url(url):
        """
        [흐름: URL 문자열 스캔 -> 패턴 매칭 -> ID 숫자 추출]
        예: https://.../recipe/6900000 -> 6900000 추출
        """
        match = re.search(r'/recipe/(\d+)', url)
        return match.group(1) if match else None