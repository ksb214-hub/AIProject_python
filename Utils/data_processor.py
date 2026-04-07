# 데이터 가공 라이브러리 (utils/data_processor.py)
# 정규표현식(re)을 사용하여 텍스트 데이터의 불필요한 공백이나 특수문자를 정제하는 전용 모듈입니다

import re

class DataCleaner:
    @staticmethod
    def clean_title(title_text):
        """레시피 제목에서 불필요한 특수문자 및 공백 제거"""
        if not title_text: return ""
        # 양끝 공백 제거 및 연속된 공백 하나로 축소
        refined = re.sub(r'\s+', ' ', title_text).strip()
        return refined

    @staticmethod
    def extract_id_from_url(url):
        """URL에서 레시피 고유 ID만 추출 (분석용)"""
        match = re.search(r'/recipe/(\d+)', url)
        return match.group(1) if match else None