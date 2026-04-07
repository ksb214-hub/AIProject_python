# driver/driver_loader.py
# 이 파일은 프로젝트의 **'엔진'**을 준비하는 곳입니다. 
# 브라우저가 보이지 않게 백그라운드에서 실행되도록 설정하고, 봇 감지를 피하기 위한 설정을 담당합니다.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_headless_driver():
    """
    [흐름: 브라우저 환경 설정 -> 드라이버 설치 -> 인스턴스 반환]
    1. 브라우저 옵션 객체 생성
    2. 사용자에게 창을 보여주지 않는 Headless 모드 등 옵션 추가
    3. 크롬 드라이버 자동 설치 및 실행
    """
    chrome_options = Options()
    
    # --- 브라우저 옵션 설정 ---
    chrome_options.add_argument("--headless")           # 브라우저 창을 띄우지 않음 (리소스 절약)
    chrome_options.add_argument("--no-sandbox")          # 리눅스 환경 등에서 보안 샌드박스 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage") # 공유 메모리 부족 오류 방지
    chrome_options.add_argument("--disable-gpu")         # 그래픽 가속 비활성화 (Headless 필수)
    
    # 실제 사람이 브라우저를 사용하는 것처럼 보이게 하는 식별자(User-Agent) 삽입
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # --- 드라이버 설치 및 반환 ---
    # ChromeDriverManager를 통해 별도의 드라이버 다운로드 없이 최신 버전 자동 유지
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver