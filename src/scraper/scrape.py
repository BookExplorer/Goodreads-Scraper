from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from src.utils.utils import (
    process_book,
    parse_infinite_status,
)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

URL = "https://www.goodreads.com/review/list/71341746?shelf=read"


def scrape_shelf(url: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)

    # Wait for initial load
    body = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    # Clicks to remove login popup.
    webdriver.ActionChains(browser).move_by_offset(10, 100).click().perform()
    # Wait for the infinite status
    infinite_status = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.ID, "infiniteStatus"))
    )
    current_books, remaining_books = parse_infinite_status(infinite_status)
    while current_books < remaining_books:
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
    book_list = [process_book(browser, book) for book in books]
    browser.quit()
    return book_list


if __name__ == "__main__":
    book_list = scrape_shelf(URL)
    print(book_list)
