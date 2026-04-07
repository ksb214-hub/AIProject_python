# driver/driver_loader.py
# 이 파일은 프로젝트의 **'엔진'**을 준비하는 곳입니다. 
# 브라우저가 보이지 않게 백그라운드에서 실행되도록 설정하고, 봇 감지를 피하기 위한 설정을 담당합니다.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_headless_driver():
    """
    [설계 의도: 독립적 브라우저 생성기]
    - 멀티스레딩 환경에서 각 스레드가 자신만의 브라우저를 가질 수 있게 합니다.
    - 리소스 점유를 최소화하기 위해 가속 옵션을 최적화했습니다.
    """
    """
    [흐름: 브라우저 환경 설정 -> 드라이버 설치 -> 인스턴스 반환]
    1. 브라우저 옵션 객체 생성
    2. 사용자에게 창을 보여주지 않는 Headless 모드 등 옵션 추가
    3. 크롬 드라이버 자동 설치 및 실행
    """
    chrome_options = Options()
    
    # --- 브라우저 성능 및 보안 옵션 ---
    chrome_options.add_argument("--headless")           # UI 없이 백그라운드에서 실행
    chrome_options.add_argument("--no-sandbox")          # 보안 샌드박스 비활성화 (Docker/Server용)
    chrome_options.add_argument("--disable-dev-shm-usage") # 메모리 부족 오류 방지
    chrome_options.add_argument("--disable-gpu")         # 그래픽 가속 꺼서 리소스 절약
    
    # --- 봇 감지 우회 설정 ---
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # --- 로딩 전략 ---
    # DOM 구조가 완성되면 즉시 제어권을 가져와 속도를 높임 (이미지 완료 대기 X)
    chrome_options.page_load_strategy = 'eager'
    
    # 드라이버 자동 설치 및 인스턴스 생성
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 네트워크 지연 시 최대 30초까지만 대기 (타임아웃 방지)
    driver.set_page_load_timeout(30) 
    
    return driver
   
   