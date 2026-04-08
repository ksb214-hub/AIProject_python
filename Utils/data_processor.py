# utils/data_processor.py
# 이 파일은 수집된 가공되지 않은 데이터를 **'정제'**하는 곳입니다. 
# 챗봇이 자연스럽게 말할 수 있도록 텍스트의 불순물을 제거하고 핵심 'Entity'를 추출합니다.

import re

class DataCleaner:
    """
    [Data Flow: Raw Text (웹 노이즈) -> Regex Filtering (정규표현식) -> Standardized Data (정형 데이터)]
    - 역할: 웹 스크래핑으로 수집된 지저분한 문자열을 정규화합니다.
    - 설계 의도: 데이터의 '본질'만 남겨 검색 엔진과 챗봇 응답의 정확도를 높이는 것입니다.
    """

    def clean_title(self, title_text):
        """
        [흐름: 제목 정제]
        1. 텍스트 내부에 포함된 불필요한 줄바꿈(\n) 및 탭(\t)을 감지합니다.
        2. 모든 연속된 공백을 단일 공백으로 치환하여 가독성을 높입니다.
        """
        if not title_text: return ""
        # r'\s+' : 백슬래시 경고 방지를 위해 Raw String 사용
        # 모든 종류의 공백 문자를 찾아서 단일 스페이스로 통일
        return re.sub(r'\s+', ' ', title_text).strip()

    def clean_material(self, material_text):
        """
        [흐름: 재료 기본 정제]
        1. 웹 페이지 버튼 텍스트인 '구매'를 제거합니다.
        2. 문자열 앞뒤의 불필요한 여백을 제거하여 "재료명 + 분량" 구조를 만듭니다.
        """
        if not material_text: return ""
        refined = re.sub(r'구매', '', material_text)
        return re.sub(r'\s+', ' ', refined).strip()

    def extract_pure_material(self, material_text):
        """
        [흐름: 재료 키워드 추출 (Entity Extraction)]
        목표: "돼지고기 300g" -> "돼지고기" (숫자와 단위를 걷어내고 식재료 본연의 이름만 추출)
        
        1. 숫자 및 분수 패턴 제거 (예: 100, 0.5, 1/2 등)
        2. 한국 요리 상용 단위 사전 패턴 제거 (예: g, 큰술, 컵 등)
        3. 부연 설명 및 특수 기호 제거 (예: /다진것, 괄호 내용 등)
        """
        if not material_text: return ""
        
        # [단계 1] 숫자 및 분수 패턴 제거 (Raw String r'' 적용으로 SyntaxWarning 해결)
        # \d+ (숫자 하나 이상), \.? (소수점 있을 수도 있음), \d* (소수점 뒤 숫자들)
        text = re.sub(r'\d+\.?\d*|\d+/\d+', '', material_text)
        
        # [단계 2] 한국 요리 상용 단위 사전 패턴 매칭 및 삭제
        unit_pattern = r'(g|kg|ml|L|컵|큰술|T|t|작은술|개|봉지|줄기|대|꼬집|줌|쪽|톨|알|근|판|장|분량|적당량|약간|숟가락|스푼)'
        text = re.sub(unit_pattern, '', text)
        
        # [단계 3] 가공 상태 설명 및 특수 기호 제거
        # /로 시작하는 설명이나 괄호 안에 든 텍스트를 공백으로 치환
        text = re.sub(r'\(.*?\)|/.*?\s', ' ', text)
        
        # [단계 4] 최종 정제: 위 과정에서 발생한 중복 공백을 하나로 합치고 양 끝 정리
        return re.sub(r'\s+', ' ', text).strip()