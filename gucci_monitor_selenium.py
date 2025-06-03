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

# Load credentials from environment variables
EMAIL = os.getenv("GUCCI_EMAIL")
PASSWORD = os.getenv("GUCCI_PASSWORD")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")

GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"
CHECK_INTERVAL = 120  # seconds

previous_items = set()

def send_push(message):
    print(f"📲 Sending push notification: {message}", flush=True)
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": "👜 Gucci Monitor",
        "priority": 1
    })

def login_and_get_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://employeestore.gucci.com/ae/en_gb/")
    print("🌐 Opened Gucci store login page.", flush=True)
    time.sleep(3)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "gl-cta--primary"))
        ).click()
        print("🔐 Clicked login button.", flush=True)

        time.sleep(2)
        driver.find_element(By.NAME, "logonId").send_keys(EMAIL)
        driver.find_element(By.NAME, "logonPassword").send_keys(PASSWORD)
        print("✏️ Entered login credentials.", flush=True)

        driver.find_element(By.CLASS_NAME, "loginForm__submit").click()
        print("✅ Submitted login form.", flush=True)
        time.sleep(5)

    except TimeoutException:
        print("⚠️ Login form not found — maybe already logged in.", flush=True)

    cookies = driver.get_cookies()
    print("🍪 Retrieved cookies.", flush=True)
    driver.quit()

    cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
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
    global previous_items
    cookie_header = login_and_get_cookies()
    send_push("✅ Gucci monitor with Selenium login started!")

    while True:
        try:
            print("🔄 Checking for new products...", flush=True)
            current_items = fetch_products(cookie_header)
            new_items = current_items - previous_items
            if new_items:
                for item in new_items:
                    msg = f"🆕 New item: https://employeestore.gucci.com{item}"
                    print(msg, flush=True)
                    send_push(msg)
                previous_items = current_items
            else:
                print("✅ No new items.", flush=True)
        except Exception as e:
            print(f"⚠️ Error occurred: {e}", flush=True)
            send_push(f"⚠️ Error: {str(e)}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
