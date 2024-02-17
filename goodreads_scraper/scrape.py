from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from goodreads_scraper.utils import (
    create_shelf_url,
    create_read_page,
    parse_infinite_status,
    setup_browser,
    is_goodreads_profile,
    read_books,
    page_wait,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
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
    body = page_wait(browser)
    # Wait for the infinite status
    infinite_status = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.ID, "infiniteStatus"))
    )
    if infinite_status.text:  # If there is text, the scroll will work.
        scroll_shelf(infinite_status, body, browser)
        book_list = read_books(browser)
    else:
        book_list = read_books(browser)
        try:
            pagination = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "reviewPagination"))
            )
            next_pages = pagination.find_elements(By.CSS_SELECTOR, "a")
            max_page = int(next_pages[-2].text)

            for i in range(2, max_page + 1):
                new_url = create_read_page(url, i)
                browser.get(new_url)
                body = page_wait(browser)
                book_list += read_books(browser)
        except TimeoutException:
            print("No pagination, single page shelf.")
        # Aí você processa cada página e vai adicionando.
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
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_profile(user_profile)
    print(books)
