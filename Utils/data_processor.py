# utils/data_processor.py
# 이 파일은 수집된 가공되지 않은 데이터를 **'정제'**하는 곳입니다. 
# 챗봇이 자연스럽게 말할 수 있도록 텍스트의 불순물을 제거합니다.

import re

class DataCleaner:
    @staticmethod
    def clean_title(title_text):
        """레시피 제목 정제 (기존 로직)"""
        if not title_text: return ""
        return re.sub(r'\s+', ' ', title_text).strip()

    @staticmethod
    def clean_material(material_text):
        """
        [흐름: 원본 텍스트 -> '구매' 키워드 제거 -> 연속 공백 정제 -> 최종 반환]
        예: "돼지갈비 900g 구매" -> "돼지갈비 900g"
        """
        if not material_text:
            return ""
        
        # 1. '구매' 단어 제거 (정규표현식 사용)
        # r'구매' 뒤에 공백이 있을 수 있으므로 처리
        refined = re.sub(r'구매', '', material_text)
        
        # 2. 양 끝 공백 제거 및 중간의 연속된 공백을 하나로 축소
        refined = re.sub(r'\s+', ' ', refined).strip()
        
        return refined