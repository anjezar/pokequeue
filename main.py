import os
import re
import time
import requests
from urllib.parse import urljoin

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID  = os.getenv('TELEGRAM_USER_ID')

URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 10  # bump up to 10s so you don’t get rate-limited

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        requests.post(url, data=data)
        print("✅ Telegram notification sent.", flush=True)
    except Exception as e:
        print("❌ Error sending Telegram:", e, flush=True)

def check_queue():
    headers = {"User-Agent": "Mozilla/5.0"}
    # 1) fetch main page
    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()
    html = r.text
    print(f"[MAIN] fetched homepage ({len(html)} bytes)", flush=True)

    # 2) extract the Incapsula iframe src
    m = re.search(r'<iframe[^>]+id="main-iframe"[^>]+src="([^"]+)"', html)
    print("[MAIN] iframe#main-iframe found?", bool(m), flush=True)
    if not m:
        return False

    iframe_src = m.group(1)
    iframe_url = urljoin(URL, iframe_src)
    print("[MAIN] queue iframe URL =", iframe_url, flush=True)

    # 3) fetch the iframe itself
    q = requests.get(iframe_url, headers=headers, timeout=10)
    q.raise_for_status()
    qtext = q.text
    print(f"[IFRAME] fetched queue page ({len(qtext)} bytes)", flush=True)

    # 4) only alert if the <title> is exactly the waiting room title
    marker = "<title>Waiting Room | Pokémon Center Official Site</title>"
    found = marker in qtext
    print(f"[IFRAME] waiting-room title present? {found}", flush=True)

    if found:
        send_telegram_alert(
            "🚨 Queue is LIVE on Pokémon Center! 🔗 https://www.pokemoncenter.com/"
        )
        return True

    return False

if __name__ == "__main__":
    print("🔍 Starting Pokémon Center queue monitor…", flush=True)
    while True:
        try:
            if check_queue():
                print("🎉 Queue detected—stopping monitor.", flush=True)
                break
        except Exception as e:
            print("❌ check_queue error:", e, flush=True)

        print(f"💤 No queue—sleeping {CHECK_INTERVAL}s", flush=True)
        time.sleep(CHECK_INTERVAL)
