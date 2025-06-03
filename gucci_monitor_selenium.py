import time
import os
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Environment variables
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"
COOKIE_HEADER = os.getenv("gucci_cookies", "")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")
GUCCI_EMAIL = os.getenv("GUCCI_EMAIL")
GUCCI_PASSWORD = os.getenv("GUCCI_PASSWORD")

previous_items = set()

def send_push_notification(msg):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": msg,
        "title": "Gucci Monitor",
        "priority": 1
    })

def fetch_products_with_selenium():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get("https://employeestore.gucci.com/ae/en_gb")

    try:
        email_input = driver.find_element(By.ID, "j_username")
        password_input = driver.find_element(By.ID, "j_password")
        email_input.send_keys(GUCCI_EMAIL)
        password_input.send_keys(GUCCI_PASSWORD)
        password_input.submit()
        time.sleep(3)
    except:
        print("Login fields not found — possibly already logged in.")

    driver.get(GUCCI_URL)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_elements = soup.find_all("div", class_="grid-tile")

    new_items = []
    for item in product_elements:
        link = item.find("a", href=True)
        if link:
            href = link["href"]
            if href not in previous_items:
                previous_items.add(href)
                new_items.append(href)

    driver.quit()

    return new_items

def run_monitor():
    print("Running cron-based Gucci monitor...")
    new_items = fetch_products_with_selenium()
    if new_items:
        send_push_notification(f"New Gucci item(s) added:\n" + "\n".join(new_items))
    else:
        send_push_notification("No new items found.")

if __name__ == "__main__":
    run_monitor()
