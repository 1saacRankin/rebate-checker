#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime
import subprocess
import os
import time

# ----------------------------
# Configuration
# ----------------------------
URL = "https://www.goelectricotherrebates.ca/eligible-vehicles?category=Cargo%20E-bikes"

# NOTICE_TEXT = (
#     "The Go Electric Rebates Program has recently received a significant volume of applications "
#     "and is currently processing them as quickly as possible. As a result, the program is not "
#     "accepting new applications at this time."
# )

NOTICE_TEXT = (
    "The CleanBC Go Electric Rebates program is currently paused. Due to high demand, available funds have been fully allocated."
    "Applications submitted prior to August 11th are being processed on a first-come, first-serve basis. No new applications are being accepted."
    "Applicants who submitted their application before August 11th and did not receive funding may be placed on a waitlist for the On-Road Medium- and Heavy-Duty Zero-Emission Vehicle category only."
    "The Fraser Basin Council will contact eligible waitlisted applicants directly to assess eligibility."
    "Please note: New applications cannot be added to the waitlist, and other vehicle categories are not eligible for this funding."
)

LOG_FILE = "/Users/isaacrankin/EbikeRebate/rebate_checker.log"
GECKODRIVER_PATH = "/opt/homebrew/bin/geckodriver"
SCREENSHOT_DIR = "/Users/isaacrankin/EbikeRebate/screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ----------------------------
# Helper Functions
# ----------------------------
def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def send_mac_notification(title: str, message: str):
    try:
        subprocess.run([
            "terminal-notifier",
            "-title", title,
            "-message", message
        ], check=True)
        log("✅ Notification sent successfully!")
    except subprocess.CalledProcessError as e:
        log(f"❌ Failed to send notification: {e}")

def normalize(text: str) -> str:
    return " ".join(text.split())

# ----------------------------
# Main Website Check
# ----------------------------
def check_website(retries=3, delay=5) -> bool:
    options = Options()
    options.headless = True
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    service = Service(executable_path=GECKODRIVER_PATH)

    try:
        driver = webdriver.Firefox(service=service, options=options)
        driver.get(URL)

        for attempt in range(1, retries + 1):
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "modal-body"))
                )

                modal_divs = driver.find_elements(By.CLASS_NAME, "modal-body")
                notice_found = False

                for i, modal in enumerate(modal_divs, start=1):
                    modal_text = driver.execute_script("return arguments[0].innerText;", modal).strip()
                    normalized_modal = normalize(modal_text)
                    normalized_notice = normalize(NOTICE_TEXT)

                    log(f"Modal #{i} text:\n{modal_text}")

                    if normalized_notice in normalized_modal:
                        notice_found = True
                        log("Conclusion: Notice present → applications CLOSED")
                        break

                if notice_found:
                    return False
                else:
                    log("Conclusion: No modal contained notice text → applications may be open")
                    return True

            except TimeoutException:
                log("Conclusion: No modal found → assuming applications CLOSED")
                return False

            time.sleep(delay)

        # If retries exhausted, save screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        log(f"Conclusion: Unexpected state after {retries} attempts. Screenshot saved: {screenshot_path}")
        return False

    except WebDriverException as e:
        log(f"Conclusion: Selenium WebDriver error: {e}")
        return False
    except Exception as e:
        log(f"Conclusion: Unexpected error: {e}")
        return False
    finally:
        driver.quit()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    if check_website():
        send_mac_notification(
            "🚨 Go Electric Rebates Update",
            "Notice disappeared! Applications may be open."
        )






# # To run: /Users/isaacrankin/EbikeRebate/run_rebate_checker.sh
# # (scrape) isaacrankin@Isaacs-MacBook-Air-2 ~ % /Users/isaacrankin/EbikeRebate/run_rebate_checker.sh

