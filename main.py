import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# Your Telegram bot credentials (loaded safely from environment variables)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 5  # Increased interval as browser automation is resource-intensive

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

# Detect the queue text using Selenium
def check_queue_selenium():
    try:
        # Set up Chrome WebDriver (you might need to configure this for your environment)
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(URL)

        # Wait for a specific element that appears when the queue is active
        # Based on your screenshot, the text "You are currently in line to enter..."
        # seems to be within a <div class="...">. You might need to inspect the
        # elements on the live page to find a reliable selector.
        try:
            wait = WebDriverWait(driver, 10)
            queue_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'You are currently in line to enter')]")))
            send_telegram_alert("⚠️ Queue is LIVE on Pokémon Center! Go now: https://www.pokemoncenter.com/")
            driver.quit()
            return True
        except:
            driver.quit()
            return False

    except Exception as e:
        print(f"Selenium Error: {e}")
        return False

# Main loop
print("🔍 Monitoring Pokémon Center using Selenium...")
while True:
    try:
        if check_queue_selenium():
            print("🚨 Queue detected! Notification sent.")
            break  # You might want to continue monitoring or stop here
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Main loop error:", e)
        time.sleep(CHECK_INTERVAL)