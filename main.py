import os
import requests
import time

# Your Telegram bot credentials (loaded safely from environment variables)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 10  # Increased interval to reduce load

# Send message to your Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    try:
        requests.post(url, data=data)
        print("Telegram notification sent.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

# Detect the queue by checking for iframe tags
def check_queue():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        if "<iframe" in response.text.lower():
            send_telegram_alert("⚠️ Possible queue forming on Pokémon Center (iframe detected)! Check it out: https://www.pokemoncenter.com/")
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return False

# Main loop
print("🔍 Monitoring Pokémon Center (checking for iframe)...")
while True:
    try:
        if check_queue():
            print("🚨 Possible queue detected (iframe found)! Notification sent.")
            break  # Or continue monitoring
        print(f"Queue not detected (no iframe). Sleeping for {CHECK_INTERVAL} seconds.")
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Main loop error:", e)
        time.sleep(CHECK_INTERVAL)