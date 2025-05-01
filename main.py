import os
import re
import time
import requests
from urllib.parse import urljoin

# Your Telegram bot credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID  = os.getenv('TELEGRAM_USER_ID')

# URLs and polling interval
URL               = "https://www.pokemoncenter.com/"
RETURN_POLICY_URL = "https://www.pokemoncenter.com/en-ca/return-policy"
CHECK_INTERVAL    = 10  # seconds

def send_telegram_alert(message):
    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        requests.post(url, data=data)
        print("✅ Telegram notification sent.")
    except Exception as e:
        print("❌ Error sending Telegram message:", e)

def check_queue():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(URL, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text

        # find the queue-iframe
        m = re.search(r'<iframe[^>]+id="main-iframe"[^>]+src="([^"]+)"', html)
        if not m:
            return False

        iframe_url = urljoin(URL, m.group(1))
        q = requests.get(iframe_url, headers=headers, timeout=10)
        q.raise_for_status()
        qtext = q.text

        # alert only on the real waiting-room title
        if "<title>Waiting Room | Pokémon Center Official Site</title>" in qtext:
            send_telegram_alert(
                "🚨 Queue is LIVE on Pokémon Center! 🔗 https://www.pokemoncenter.com/"
            )
            return True

    except Exception as e:
        print("check_queue error:", e)
    return False

def check_return_policy():
    try:
        r = requests.get(RETURN_POLICY_URL, timeout=10)
        r.raise_for_status()
        if "Return Policy" not in r.text:
            send_telegram_alert(
                "⚠️ The Return Policy page is missing its header! "
                f"Check {RETURN_POLICY_URL}"
            )
            return True
    except Exception as e:
        print("check_return_policy error:", e)
    return False

if __name__ == "__main__":
    print("🔍 Monitoring Pokémon Center…")
    while True:
        # 1) check for queue
        if check_queue():
            # queue-alert was already sent inside check_queue()
            break

        # 2) check for missing Return Policy text
        try:
            resp = requests.get(RETURN_POLICY_URL, timeout=10)
            resp.raise_for_status()
            if "Return Policy" not in resp.text:
                send_telegram_alert(
                    "⚠️ Return Policy page broken or missing its header! "
                    f"Check {RETURN_POLICY_URL}"
                )
                break
        except Exception as e:
            print("check_return_policy error:", e)

        time.sleep(CHECK_INTERVAL)

