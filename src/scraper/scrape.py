import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from math import ceil, inf
import time
from src.utils.utils import (
    extract_hidden_td,
    extract_author_id,
    process_book,
    parse_infinite_status,
)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def wait_for_more_books(driver, previous_count) -> bool:
    """Custom wait condition to check if more books have loaded."""
    try:
        # Wait for up to 10 seconds (or your preferred timeout)
        WebDriverWait(driver, 10).until(
            lambda x: len(driver.find_elements(By.CLASS_NAME, "bookalike"))
            > previous_count
        )
        return True
    except TimeoutException:
        return False


browser = webdriver.Chrome()

URL = "https://www.goodreads.com/review/list/71341746?shelf=read"
browser.get(URL)

# Wait for initial load
WebDriverWait(browser, 10)
# Clicks to remove login popup.
webdriver.ActionChains(browser).move_by_offset(10, 100).click().perform()
# Wait for the infinite status
infinite_status = WebDriverWait(browser, 5).until(
    lambda x: x.find_element(By.ID, "infiniteStatus")
)
current_books, remaining_books = parse_infinite_status(infinite_status)
body = browser.find_element(By.TAG_NAME, "body")
while current_books <= remaining_books:
    # Scroll down
    body.send_keys(Keys.END)

    # Get updated status
    WebDriverWait(browser, 10).until(
        lambda x: len(x.find_elements(By.CLASS_NAME, "bookalike")) > current_books
    )
    infinite_status = WebDriverWait(browser, 5).until(
        lambda x: x.find_element(By.ID, "infiniteStatus")
    )
    current_books, _ = parse_infinite_status(infinite_status)


books = browser.find_elements(By.CLASS_NAME, "bookalike")

# Example:
book = books[0]


print(process_book(browser, book))

browser.quit()

print(2)
