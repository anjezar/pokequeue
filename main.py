import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import requests

# Your Telegram bot credentials (loaded safely from environment variables)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

# Target URL and interval
URL = "https://www.pokemoncenter.com/"
CHECK_INTERVAL = 5  # Increased interval as browser automation is resource-intensive

# Send message to your Telegram
def send_telegram_alert(message):
    print(f"Inside send_telegram_alert() with message: {message}")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Telegram notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

# Detect the queue text using Selenium
def check_queue_selenium():
    print("Inside check_queue_selenium()")
    try:
        # Set up Chrome WebDriver in headless mode for Render
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # Required for running Chrome as root
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver initialized successfully in headless mode.")
        driver.get(URL)
        print(f"Successfully loaded URL: {URL}")

        # Wait for a specific element that appears when the queue is active
        # Based on your screenshot, the text "You are currently in line to enter..."
        # seems to be within a <div class="...">. You might need to inspect the
        # elements on the live page to find a reliable selector.
        try:
            wait = WebDriverWait(driver, 10)
            queue_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'You are currently in line to enter')]")))
            print("Queue element found!")
            send_telegram_alert("⚠️ Queue is LIVE on Pokémon Center! Go now: https://www.pokemoncenter.com/")
            driver.quit()
            return True
        except Exception as e:
            print(f"Queue element not found within timeout: {e}")
            driver.quit()
            return False

    except Exception as e:
        print(f"Selenium Error in check_queue_selenium(): {e}")
        return False

# Main loop
print("🔍 Monitoring Pokémon Center using Selenium...")
while True:
    try:
        print("About to call check_queue_selenium()")
        if check_queue_selenium():
            print("🚨 Queue detected! Notification sent. Exiting loop (you can change this).")
            break  # You might want to continue monitoring or stop here
        print(f"Queue not detected. Sleeping for {CHECK_INTERVAL} seconds.")
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print("Main loop error:", e)
        time.sleep(CHECK_INTERVAL)