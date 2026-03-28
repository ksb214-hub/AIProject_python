from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver(headless=True):
    options = Options()

    if headless:
        options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    return driver