import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = "7696717269:AAG65MsL8MkRn8Lp1QipGozqbuLOmNvS-I8"
TELEGRAM_USER_ID = "1707682850"
GUCCI_EMAIL = os.getenv("GUCCI_EMAIL")
GUCCI_PASSWORD = os.getenv("GUCCI_PASSWORD")
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def login_and_get_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://employeestore.gucci.com/ae/en_gb/")
    time.sleep(3)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "gl-cta--primary"))
        ).click()

        time.sleep(2)
        driver.find_element(By.NAME, "logonId").send_keys(GUCCI_EMAIL)
        driver.find_element(By.NAME, "logonPassword").send_keys(GUCCI_PASSWORD)
        driver.find_element(By.CLASS_NAME, "loginForm__submit").click()
        time.sleep(5)

    except TimeoutException:
        print("Login form not found — maybe already logged in.")

    cookies = driver.get_cookies()
    driver.quit()
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    return cookie_str

def fetch_products(cookie_header):
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(GUCCI_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.select("a.teaser__anchor")
    return {p["href"] for p in products if "href" in p.attrs}

def main():
    send_telegram("🚀 Gucci Monitor via Telegram started")
    cookie_header = login_and_get_cookies()
    products = fetch_products(cookie_header)
    for p in products:
        send_telegram(f"🆕 New item: https://employeestore.gucci.com{p}")

if __name__ == "__main__":
    main()
