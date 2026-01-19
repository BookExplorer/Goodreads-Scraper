from selenium.webdriver.chrome.webdriver import WebDriver
import json
from selenium.webdriver.common.by import By
import os
from pathlib import Path


COOKIE_FILE = Path("login.json")

def read_cookies(browser: WebDriver) -> bool:
    """
    Tries to load cookies into the browser.
    Returns True if cookies were loaded, False otherwise.
    """
    if not COOKIE_FILE.exists():
        return False

    with COOKIE_FILE.open("r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        browser.add_cookie(cookie)

    return True

def login(browser: WebDriver) -> None:
    browser.get('https://www.goodreads.com/user/sign_in')
    login_modal = browser.find_element(By.XPATH, "//button[contains(text(), 'Sign in with email')]")
    login_modal.click()
    email_field = browser.find_element(By.XPATH,"//input[@type='email']")
    email = os.environ['GR_LOGIN']
    email_field.send_keys(email)
    password_field = browser.find_element(By.XPATH,"//input[@type='password']")
    password = os.environ['GR_PASSWORD']
    password_field.send_keys(password)
    submit_field = browser.find_element(By.XPATH,"//input[@type='submit']")
    submit_field.click()


def save_cookies(browser: WebDriver) -> None:
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with COOKIE_FILE.open("w") as f:
        json.dump(browser.get_cookies(), f)


def authenticate(browser: WebDriver, url: str) -> None:
    cookies_loaded = read_cookies(browser)
    browser.get(url)
    if 'sign_in' in browser.current_url or not cookies_loaded:
        # If you get redirected to sign in, you need to actually login and then save the cookies, as they have most likely expired.
        login(browser)
        browser.get(url)
    if 'sign_in' in browser.current_url:
        raise RuntimeError('Login failed.')
    save_cookies(browser) # Only if login is ok do you save cookies.