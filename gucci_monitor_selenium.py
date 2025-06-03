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

GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"
CHECK_INTERVAL = 120  # seconds

GUCCI_EMAIL = os.getenv("GUCCI_EMAIL")
GUCCI_PASSWORD = os.getenv("GUCCI_PASSWORD")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")

previous_items = set()

def send_push(message):
    print("🔔 Sending push notification...")
    try:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_APP_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "👜 Gucci Monitor",
            "priority": 1
        })
    except Exception as e:
        print(f"❌ Failed to send push: {e}")

def login_and_get_cookies():
    print("🔐 Launching headless Chrome and logging in...", flush=True)
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
        print("🔓 Clicked login button.", flush=True)

        time.sleep(2)
        driver.find_element(By.NAME, "logonId").send_keys(GUCCI_EMAIL)
        driver.find_element(By.NAME, "logonPassword").send_keys(GUCCI_PASSWORD)
        print("📝 Entered credentials.")

        driver.find_element(By.CLASS_NAME, "loginForm__submit").click()
        print("🚀 Submitted login form.")
        time.sleep(5)
    except TimeoutException:
        print("⚠️ Login form not found — maybe already logged in.")

    cookies = driver.get_cookies()
    print("🍪 Retrieved cookies.")
    driver.quit()

    return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

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
            print("🔁 Checking for new products...", flush=True)
            current_items = fetch_products(cookie_header)
            new_items = current_items - previous_items
            if new_items:
                for item in new_items:
                    msg = f"🆕 New item: https://employeestore.gucci.com{item}"
                    print(msg)
                    send_push(msg)
                previous_items = current_items
            else:
                print("✅ No new items found.")
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            send_push(f"⚠️ Error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
