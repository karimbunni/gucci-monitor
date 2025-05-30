import requests
from bs4 import BeautifulSoup
import time

# === USER SETTINGS ===
GUCCI_URL = "https://employeestore.gucci.com/ae/en_gb/ca/new-in-c-new-in"
COOKIE_HEADER = "token=exp=1748562406~acl=%2f*~hmac=3168a3ea6136f3582492f91f66db9b894e5c6212ab6753549e2a17e2cb823475; _troruid=3e488f60-b058-4285-9990-1c4666344b6e; _trossion=1748555216_1800_13e488f60-b058-4285-9990-1c4666344b6e%3A1748555216_1748555229_2; _abck=D6BA860F13A19F28E615D7EED07E5A78~-1~YAAQvxjdWMbJTfqWAQAABWQBHg3iJ2ApvYTS+5NddwNZObmsXEgo4cVBXPccisMVQo+iqGFn3upt/90Dfk7NpLKjRgrJsOgoAVG0omhi/FwglYCSwLyJOX89JRSZBtPGgvn3LmFIzhJxDHTX8EuaThxyhTq+TUC+E2IwjyCQW/NO9e3BMxnzVlMuU9kskKGCLt90pmrY/k2CEdvDXJN3w7rxX2aymfkwofE9GR4ad1sDh5G+j24H2Tkzy6UwDrxZVA3QOCn7iQpKReYkYlWJauFd2zn+XUC39Kj+kgrJ1gdMuiiDyzpRJSnEv3n0AFqp5DDRsVRpT/VOFu6NC3xrF4dIknDibifMs97lb1dURAamZpW1EGTzkNZm67yhPfMfbgxWOjV7t34uOURojvaM3cEjX1LiJehxA6PSm+0ClOJzffqlrwMtZ5FqFKzRsG4zb1AR~-1~-1~-1; _dd_s=logs=1&id=694b0d78-cfbb-4492-a940-1e2c6bd6187a&created=1748555107163&expire=1748557019880; _ga=GA1.1.1884246792.1748555109; awslab=ifk404/QKImADyt2M4oq9K31OjWdiKOBxpmFEAWH3nXWL/VMokCYZ8RxHiSOJuuPm+zYVIfH63HyTR/97g4Nkk+2sDHkEvxS1cq/hDchXX2vNXtSn/8qUcGuI7hJ; bm_sz=230A53D1621FDE7B9A6D05460938E606~YAAQLecVAjK7sPCWAQAAkPUDHhsRSPoIJuLqM+WN6+jjIrizmuDn4AfFm7CL4pew5LgLQl7iBrlqCueSmv6FFYIY0yKGE9QYi5anF8AteKir8yJHzJXrMAB+heUQE4vJtpLf8OSUfLNPAF/nV/uPuc9+tD1PI/kSCQ6fcuSQq/puNrBuFYxKOJdCOvzCdLt9QQjFrHAVsHOmBxDgFBB4H/W6Hnc3z6OhyYjSsfbUjMuU/tQ/yd+uJ7ktbiCaxEekdxYEhBbevKgiwC3xXPfIcyVBi+Sm5e2byx6TrEfbNt4qxkOKRS1gcTae4/aqshLke00pCDITmg2dMET4B0NGSqDXi6KG86c8rPsyeOU8teSzg46mr6EHngoCPkZ8tzxDlGwezq0cNzXS0YMboj5co7aFJpFS2oCa9lGP/SgAMbCAQvVg5Zeq7pmiAlO7UOpM3ET0026Iet+hOZtcWpb/tGY8EmA+oHWjkrsxawDVIHRIkk0trNdnS9/iIfk=~4342069~3228998; jsessionid=3E422D77DCFE406684C3C953A58C6028-n2; voxsessionid=7c144f69-458a-4eec-8f27-946558e607ea"
PUSHOVER_USER_KEY = "u9xa674xdqx6zdefodtpz9tdbwhw5p"
PUSHOVER_APP_TOKEN = "acemf778z6u1fr9u14vp9zuvudbdcg"
CHECK_INTERVAL = 120  # Check every 2 minutes

# === Setup ===
previous_items = set()

def send_push(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": "👜 Gucci Monitor",
        "priority": 1
    })

def fetch_products():
    headers = {
        "Cookie": COOKIE_HEADER,
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(GUCCI_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    product_elements = soup.find_all("div", class_="grid-tile")

    products = set()
    for product in product_elements:
        title = product.get_text(strip=True)
        if title:
            products.add(title)
    return products

# === Main Loop ===
print("📡 Starting Gucci Monitor...")
while True:
    try:
        current_items = fetch_products()
        new_items = current_items - previous_items

        if new_items:
            print(f"🛍️ New products found: {len(new_items)}")
            send_push(f"New Gucci product(s): {', '.join(list(new_items)[:3])}...")
        else:
            print("No new items yet.")

        previous_items = current_items
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"❌ Error: {e}")
        send_push(f"Gucci Monitor Error: {e}")
        time.sleep(CHECK_INTERVAL)