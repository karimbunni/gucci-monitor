import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# CONFIG
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"
GUCCI_COOKIES = os.getenv("GUCCI_COOKIES")  # Entire cookie string as one line
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")
CHECK_INTERVAL = 120  # seconds

previous_products = set()

def get_headers():
    return {
        "Cookie": GUCCI_COOKIES,
        "User-Agent": "Mozilla/5.0"
    }

def send_push_notification(title, message):
    if PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_APP_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message
        })

def fetch_product_links():
    response = requests.get(GUCCI_URL, headers=get_headers())
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("a[href*='/ae/en_gb/ca/']")  # basic filter
    return set("https://employeestore.gucci.com" + a["href"] for a in links if a["href"].startswith("/ae/en_gb/ca/"))

def main():
    global previous_products
    while True:
        try:
            current_products = fetch_product_links()
            new_items = current_products - previous_products

            if new_items:
                for link in new_items:
                    send_push_notification("👜 New Gucci Item!", link)
                previous_products = current_products

        except Exception as e:
            send_push_notification("❌ Gucci Monitor Error", str(e))

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
