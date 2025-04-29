import os
import requests
import time
from bs4 import BeautifulSoup  # ✅ this line is the fix!

# Your Telegram bot credentials (loaded safely from environment variables)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 1  # check every second

# Send message to your Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    requests.post(url, data=data)

# Detect the queue via page <title>
def check_queue():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.title.string if soup.title else ""

    if "Waiting Room" in title:
        send_telegram_alert("⚠️ Queue is LIVE on Pokémon Center! Go now: https://www.pokemoncenter.com/")
        return True

    return False

# Main loop
print("🔍 Monitoring Pokémon Center...")
while True:
    try:
        if check_queue():
            print("🚨 Queue detected! Notification sent.")
            break  # optional: remove this to keep running after detection
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Error:", e)
        time.sleep(CHECK_INTERVAL)


