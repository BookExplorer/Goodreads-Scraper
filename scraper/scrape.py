import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from math import ceil
import time

from selenium.webdriver.support.ui import WebDriverWait

browser = webdriver.Chrome()

URL = "https://www.goodreads.com/review/list/71341746?shelf=read"
browser.get(URL)

# Wait for initial load
WebDriverWait(browser, 10)
# Clicks to remove login popup.
webdriver.ActionChains(browser).move_by_offset(10, 10).click().perform()
time.sleep(2)  # Wait after click to allow any actions to complete

while True:
    # Scroll down
    browser.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)  # Adjust this delay as needed

    # Get updated status
    infinite_status = browser.find_element(By.ID, "infiniteStatus")
    infinite_status_text = infinite_status.text.split(" ")
    remaining_books = int(infinite_status_text[2])
    current_books = int(infinite_status_text[0])

    print(f"Loaded {current_books} of {remaining_books} books")

    # Check if all books are loaded
    if current_books >= remaining_books:
        break

# Now you can scrape the loaded content
# Use browser.page_source to get the HTML content
# ...

# Don't forget to close the browser once done
browser.quit()
# soup = BeautifulSoup(response.content, "html.parser")
# table = soup.find("table", id="books")
# tbody = table.find("tbody", id="booksBody")
# infinite_status = soup.find(id="infiniteStatus")
print(2)
