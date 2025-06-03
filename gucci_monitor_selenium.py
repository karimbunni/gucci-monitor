import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
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
        print("Sending message to Telegram…")
        res = requests.post(url, data=payload)
        print("Telegram response:", res.status_code, res.text)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def login_and_get_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://employeestore.gucci.com/ae/en_gb/login")
        time.sleep(5)

        if "login" in driver.current_url:
            email_input = driver.find_element(By.NAME, "j_username")
            password_input = driver.find_element(By.NAME, "j_password")

            email_input.send_keys(GUCCI_EMAIL)
            password_input.send_keys(GUCCI_PASSWORD)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            print("Logged in to Gucci store.")
        else:
            print("Already logged in or login not required.")

        cookies = driver.get_cookies()
        cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        return cookie_str

    except Exception as e:
        send_telegram(f"❌ Login failed: {str(e)}")
        return None

    finally:
        driver.quit()

def monitor_gucci():
    send_telegram("✅ Gucci monitor started with Telegram notifications.")

    cookies = login_and_get_cookies()
    if not cookies:
        print("Failed to retrieve cookies.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookies,
    }

    try:
        response = requests.get(GUCCI_URL, headers=headers)
        if "New In" in response.text:
            send_telegram("🆕 Gucci website is updated with new products!")
        else:
            print("No new products detected.")
    except Exception as e:
        send_telegram(f"❌ Error checking Gucci site: {str(e)}")

if __name__ == "__main__":
    monitor_gucci()
