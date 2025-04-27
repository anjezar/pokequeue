import requests
import time

# Your Telegram bot credentials
TELEGRAM_BOT_TOKEN = '7735012081:AAHMDbOKr7zhXUGPAIdDemANqltt33f-jxw'
TELEGRAM_USER_ID = '-1002636918821'  # GROUP ID

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 1  # check every 60 seconds (set back to 60 not 1)

# Send message to your Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    requests.post(url, data=data)

# Detect the queue text
def check_queue():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    if "You are currently in line to enter Pokémon Center" in response.text:
        send_telegram_alert("⚠️ Queue is LIVE on Pokémon Center! Go now: https://www.pokemoncenter.com/")
        return True
    return False

# Main loop
print("🔍 Monitoring Pokémon Center...")
while True:
    try:
        if check_queue():
            print("🚨 Queue detected! Notification sent.")
            break
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Error:", e)
        time.sleep(CHECK_INTERVAL)
