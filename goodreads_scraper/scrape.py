from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from goodreads_scraper.utils import (
    create_shelf_url,
    process_book,
    parse_infinite_status,
    setup_browser,
    is_goodreads_profile,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List


def scroll_shelf(
    infinite_status: WebElement, body: WebElement, browser: WebDriver
) -> None:
    """Scrolls shelf until all books have been loaded.

    Args:
        infinite_status (WebElement): Element at the bottom of the page that gives the number of books loaded.
        body (WebElement): Body element of the webpage.
        browser (WebDriver): Browser being used by Selenium to scrape.
    """
    current_books, remaining_books = parse_infinite_status(infinite_status)
    while current_books < remaining_books:
        # Scroll down
        body.send_keys(Keys.END)
        # Get updated status
        WebDriverWait(browser, 10).until(
            lambda x: len(x.find_elements(By.CLASS_NAME, "bookalike")) > current_books
        )
        infinite_status = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "infiniteStatus"))
        )

        current_books, _ = parse_infinite_status(infinite_status)


def scrape_shelf(url: str) -> List[Dict[str, any]]:
    """Performs the extraction of all the books from a valid shelf URL.

    Args:
        url (str): Valid URL for a shelf.

    Returns:
        List[Dict[str, any]]: List of dictionaries where each is a book extracted from the shelf and processed accordingly.
    """
    browser = setup_browser()
    browser.get(url)

    # Wait for initial load
    body = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    # Clicks to remove login popup.
    webdriver.ActionChains(browser).move_by_offset(10, 100).click().perform()
    # Wait for the infinite status
    infinite_status = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.ID, "infiniteStatus"))
    )
    scroll_shelf(infinite_status, body, browser)
    books = browser.find_elements(By.CLASS_NAME, "bookalike")
    book_list = [process_book(browser, book) for book in books]
    browser.quit()
    return book_list


def process_profile(user_profile: str) -> List[Dict[str, str]]:
    """Main function for the scraping.
    Will get a url, validate it as a GR profile and, if valid, create the shelf url to then be scraped.
    Returns the list of books in that shelf.

    Args:
        user_profile (str): URL to be scraped, expected to be a valid GR profile.

    Raises:
        ValueError: If it's not a valid GR profile.

    Returns:
        List[Dict[str, str]]: List of dictionaries where each is a book extracted from the shelf and processed accordingly.
    """
    valid_profile = is_goodreads_profile(user_profile)
    if not valid_profile:
        raise ValueError("Your URL was not a valid Goodreads profile.")
    read_shelf_url = create_shelf_url(user_profile)
    user_books = scrape_shelf(read_shelf_url)
    return user_books


if __name__ == "__main__":
    user_profile = input("Please input your profile.")
    books = process_profile(user_profile)
    print(books)
