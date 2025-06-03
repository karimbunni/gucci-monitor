import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Environment Variables
GUCCI_EMAIL = os.environ.get("GUCCI_EMAIL")
GUCCI_PASSWORD = os.environ.get("GUCCI_PASSWORD")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.environ.get("PUSHOVER_APP_TOKEN")
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"

def send_notification(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": "Gucci Monitor",
        "priority": 1
    })

def fetch_products():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://employeestore.gucci.com/ae/en_gb/account/login")

        try:
            email_input = driver.find_element(By.ID, "email")
            password_input = driver.find_element(By.ID, "pass")
            login_button = driver.find_element(By.ID, "send2")
            email_input.send_keys(GUCCI_EMAIL)
            password_input.send_keys(GUCCI_PASSWORD)
            login_button.click()
            time.sleep(3)
        except NoSuchElementException:
            print("Login form not found (may already be logged in)")

        send_notification("✅ Gucci Monitor Login Success - Running Check...")

        driver.get(GUCCI_URL)
        page_source = driver.page_source
        driver.quit()
        return page_source

    except Exception as e:
        send_notification(f"❌ Error: {str(e)}")
        print("Error:", e)
        return None

def main():
    print("Running cron-based Gucci monitor...")
    fetch_products()

if __name__ == "__main__":
    main()
