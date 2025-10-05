"""
Selenium test script to add multiple dummy credentials.

Usage:
  - Edit the selector variables in the CONFIG section to match your app's HTML.
  - Install requirements: pip install -r requirements.txt (see message below for contents)
  - Run: python selenium.py --count 20

By default this script assumes your app runs at http://127.0.0.1:5000/ and the login form
is on the root path. Adjust base_url and selectors as needed.

This uses webdriver-manager to auto-install ChromeDriver. If you prefer Firefox, I can adapt.
"""

import time
import secrets
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------- CONFIG - update these to match your HTML structure --------
base_url = "http://127.0.0.1:5000"
login_page = "/"  # page containing the login form
# login form selectors
username_selector = "input[name='username']"
password_selector = "input[name='password']"
login_submit_selector = "button[type='submit']"  # CSS selector for the login button

# selectors for the add-overlay on the homepage (matches the HTML you pasted)
# the script will click the floating add-button, wait for the overlay, then fill and submit the form
add_button_selector = ".add-button"
overlay_form_selector = "#add-overlay form"
app_name_selector = "#add-overlay input[name='app_name']"
cred_username_selector = "#add-overlay input[name='username']"
cred_password_selector = "#add-overlay input[name='password']"
cred_email_selector = "#add-overlay input[name='email']"
cred_phone_selector = "#add-overlay input[name='phone']"
cred_icon_selector = "#add-overlay input[name='icon_filename']"
add_submit_selector = "#add-overlay form button[type='submit']"

# Optional success indicator to wait for after adding (CSS selector or None)
success_indicator_selector = None  # e.g. ".toast-success" or "#success-msg"
# -------------------------------------------------------------------

WAIT_TIMEOUT = 10


def make_driver(headless=False, browser='chrome', driver_path=None):
    """Create a webdriver instance.

    browser: 'chrome' or 'edge'
    driver_path: optional filesystem path to the webdriver executable; if provided,
                 the script will use that instead of webdriver-manager.
    """
    if browser not in ('chrome', 'edge'):
        raise ValueError("Unsupported browser: choose 'chrome' or 'edge'")

    if browser == 'chrome':
        opts = webdriver.ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
            opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        if driver_path:
            service = ChromeService(driver_path)
        else:
            service = ChromeService(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=opts)

    else:  # edge
        opts = EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
            opts.add_argument("--disable-gpu")

        if driver_path:
            service = EdgeService(driver_path)
            driver = webdriver.Edge(service=service, options=opts)
        else:
            # webdriver-manager can also install msedgedriver via webdriver_manager
            try:
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=opts)
            except Exception:
                raise RuntimeError("Edge webdriver installation failed; provide --driver-path to a local msedgedriver executable")

    driver.set_window_size(1200, 800)
    return driver


def generate_dummy_credentials(count):
    out = []
    for i in range(1, count + 1):
        app = f"TestApp_{i}"
        pwd = secrets.token_urlsafe(12)
        out.append((app, pwd))
    return out


def login(driver, username, password):
    driver.get(base_url + login_page)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    # Wait for username field
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))

    driver.find_element(By.CSS_SELECTOR, username_selector).clear()
    driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(username)
    driver.find_element(By.CSS_SELECTOR, password_selector).clear()
    driver.find_element(By.CSS_SELECTOR, password_selector).send_keys(password)

    # click submit
    driver.find_element(By.CSS_SELECTOR, login_submit_selector).click()

    # wait until homepage loads by waiting for the add button to appear
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, add_button_selector))
        )
    except Exception:
        # fallback small sleep if the selector isn't present immediately
        time.sleep(1)


def add_credential(driver, app_name, credential):
    """Open the add-overlay, fill fields and submit.

    credential here is used for the password field; username/email/phone are left blank or reused.
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # Click the floating add button to open overlay
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, add_button_selector)))
    driver.find_element(By.CSS_SELECTOR, add_button_selector).click()

    # Wait for the overlay form to appear
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, overlay_form_selector)))

    # Fill fields
    driver.find_element(By.CSS_SELECTOR, app_name_selector).clear()
    driver.find_element(By.CSS_SELECTOR, app_name_selector).send_keys(app_name)

    # use the same credential for the username field to keep things simple for testing
    driver.find_element(By.CSS_SELECTOR, cred_username_selector).clear()
    driver.find_element(By.CSS_SELECTOR, cred_username_selector).send_keys(app_name + "_user")

    driver.find_element(By.CSS_SELECTOR, cred_password_selector).clear()
    driver.find_element(By.CSS_SELECTOR, cred_password_selector).send_keys(credential)

    # optional fields - leave blank or fill with placeholders
    driver.find_element(By.CSS_SELECTOR, cred_email_selector).clear()
    driver.find_element(By.CSS_SELECTOR, cred_email_selector).send_keys(app_name.lower() + "@example.com")

    driver.find_element(By.CSS_SELECTOR, cred_phone_selector).clear()
    driver.find_element(By.CSS_SELECTOR, cred_phone_selector).send_keys("+10000000000")

    driver.find_element(By.CSS_SELECTOR, cred_icon_selector).clear()
    driver.find_element(By.CSS_SELECTOR, cred_icon_selector).send_keys("default.png")

    # Submit the form (Save button inside the overlay form)
    driver.find_element(By.CSS_SELECTOR, add_submit_selector).click()

    # wait briefly for the overlay to disappear or for main grid to update
    time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="testuser", help="login username")
    parser.add_argument("--password", default="password", help="login password (plain) - must exist in DB)")
    parser.add_argument("--count", type=int, default=10, help="how many dummy credentials to add")
    parser.add_argument("--headless", action="store_true", help="run browser headless")
    parser.add_argument("--browser", choices=["chrome", "edge"], default="chrome", help="browser to use (chrome or edge)")
    parser.add_argument("--driver-path", default=None, help="optional path to a webdriver executable (chromedriver or msedgedriver)")
    args = parser.parse_args()

    creds = generate_dummy_credentials(args.count)

    driver = make_driver(headless=args.headless, browser=args.browser, driver_path=args.driver_path)
    try:
        print(f"Logging in as {args.username}")
        login(driver, args.username, args.password)

        for i, (app, pwd) in enumerate(creds, start=1):
            print(f"Adding {i}/{len(creds)}: {app}")
            add_credential(driver, app, pwd)
            # small delay between additions to mimic a user
            time.sleep(0.5)

        print("Done adding credentials")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
