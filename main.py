import os
import re
import time
import requests
from urllib.parse import urljoin

# Your Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID  = os.getenv('TELEGRAM_USER_ID')

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 1  # seconds

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    try:
        requests.post(url, data=data)
        print("Telegram notification sent.")
    except Exception as e:
        print("Error sending Telegram message:", e)

def check_queue():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # 1) fetch the main page
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text

        # 2) find the queue iframe src
        m = re.search(r'<iframe[^>]+id="main-iframe"[^>]+src="([^"]+)"', html)
        if not m:
            # no queue iframe at all
            return False

        iframe_src = m.group(1)
        iframe_url = urljoin(URL, iframe_src)

        # 3) fetch the iframe content
        q = requests.get(iframe_url, headers=headers, timeout=10)
        q.raise_for_status()
        qtext = q.text

        # 4) detect real queue markers
        if (
            "Waiting Room | Pokémon Center Official Site" in qtext
            or "DeliveryPikachu_Wave.svg" in qtext
        ):
            send_telegram_alert(
                "🚨 Queue is LIVE on Pokémon Center! Head there now: https://www.pokemoncenter.com/"
            )
            return True

        return False

    except Exception as e:
        print("check_queue error:", e)
        return False

if __name__ == "__main__":
    print("🔍 Monitoring Pokémon Center for queue…")
    while True:
        if check_queue():
            break
        time.sleep(CHECK_INTERVAL)