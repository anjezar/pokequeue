import os
import requests
import time

# Your Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID  = os.getenv('TELEGRAM_USER_ID')

URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 10

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

def check_queue():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()

        html = r.text
        # only alert when the real queue-iframe appears
        if 'id="main-iframe"' in html and 'Incapsula_Resource' in html:
            send_telegram_alert(
                "⚠️ Queue is live! Pokémon Center is routing traffic through the queue iframe."
            )
            return True

        return False

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Monitoring Pokémon Center…")
    while True:
        if check_queue():
            break
        print(f"No queue—sleeping {CHECK_INTERVAL}s.")
        time.sleep(CHECK_INTERVAL)
