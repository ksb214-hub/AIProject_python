# Utils/ssl_helper.py

import ssl

def disable_ssl_verification():
    """
    SSL 인증서 검증을 무시하도록 설정
    Mac/Windows 환경에서 HTTPS 접속 오류 방지
    """
    ssl._create_default_https_context = ssl._create_unverified_context