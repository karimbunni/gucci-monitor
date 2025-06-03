import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Load environment variables
load_dotenv()
EMAIL = os.getenv("GUCCI_EMAIL")
PASSWORD = os.getenv("GUCCI_PASSWORD")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"

# Track items across runs
STORAGE_FILE = "seen_items.txt"

def send_push(message):
    try:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_APP_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "👜 Gucci Monitor",
            "priority": 1
        })
    except Exception as e:
        print(f"Push failed: {e}", flush=True)

def login_and_get_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://employeestore.gucci.com/ae/en_gb/")
    print("Opened Gucci login page", flush=True)
    time.sleep(3)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "gl-cta--primary"))
        ).click()
        time.sleep(2)
        driver.find_element(By.NAME, "logonId").send_keys(EMAIL)
        driver.find_element(By.NAME, "logonPassword").send_keys(PASSWORD)
        driver.find_element(By.CLASS_NAME, "loginForm__submit").click()
        print("Logged in", flush=True)
        time.sleep(5)
    except TimeoutException:
        print("Login form not found (may already be logged in)", flush=True)

    cookies = driver.get_cookies()
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

def load_seen_items():
    if not os.path.exists(STORAGE_FILE):
        return set()
    with open(STORAGE_FILE, "r") as file:
        return set(file.read().splitlines())

def save_seen_items(items):
    with open(STORAGE_FILE, "w") as file:
        file.write("\n".join(items))

def main():
    print("Running cron-based Gucci monitor...", flush=True)
    cookie_header = login_and_get_cookies()
    seen_items = load_seen_items()
    current_items = fetch_products(cookie_header)
    new_items = current_items - seen_items

    if new_items:
        for item in new_items:
            full_url = f"https://employeestore.gucci.com{item}"
            send_push(f"🆕 New item: {full_url}")
        save_seen_items(current_items)
    else:
        print("No new items found.", flush=True)

    print("Script finished cleanly.", flush=True)

if __name__ == "__main__":
    main()
