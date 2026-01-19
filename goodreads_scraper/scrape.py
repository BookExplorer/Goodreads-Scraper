from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from goodreads_scraper.utils import (
    create_read_shelf_url,
    create_read_page,
    parse_infinite_status,
    setup_browser,
    is_goodreads_profile,
    read_books_fast,
    page_wait,
    cleanup_birthplace,
    is_goodreads_shelf,
    read_cookies
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Dict, List, Any
import re
from logger import logger


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


def scrape_shelf(url: str, debug: bool = False) -> List[Dict[str, Any]]:
    """Performs the extraction of all the books from a valid shelf URL.

    Args:
        url (str): Valid URL for a shelf.

    Returns:
        List[Dict[str, any]]: List of dictionaries where each is a book extracted from the shelf and processed accordingly.
    """
    browser = setup_browser(debug=debug)
    browser.get(url)
    read_cookies(browser)
    browser.get(url)
    # Wait for initial load
    body = page_wait(browser)
    
    # Wait for the infinite status
    try:
        infinite_status = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "infiniteStatus"))
        )
        infinite_status_text = infinite_status.text
    except TimeoutException:
        logger.debug("Infinite status timeout.")
        infinite_status_text = None
    if infinite_status_text:  # If there is text, the scroll will work.
        scroll_shelf(infinite_status, body, browser)
        book_list = read_books_fast(browser)
    else:
        book_list = read_books_fast(browser)
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
                book_list += read_books_fast(browser)
        except TimeoutException:
            logger.debug("No pagination, single page shelf.")
        # Aí você processa cada página e vai adicionando.
    browser.quit()
    return book_list


def process_goodreads_url(url: str) -> List[Dict[str, str]]:
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
    valid_profile = is_goodreads_profile(url)
    valid_shelf = is_goodreads_shelf(url)
    if not valid_profile and not valid_shelf:
        raise ValueError("Your URL was not a valid Goodreads URL to scrape.")
    shelf_url = create_read_shelf_url(url) if not valid_shelf else url
    user_books = scrape_shelf(shelf_url)
    return user_books


def scrape_gr_author(url: str) -> tuple[str | None, str | None]:
    """
    Scrapes the author's Goodreads page and extracts the author's birthplace.
    Args:
        url (str): The author's Goodreads URL, brought from the scraping of the user's page.

    Returns:
        str | None: Birthplace of the author or None if we can't find it in the authors page.
    """

    browser = setup_browser()

    browser.get(url)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    try:
        born_label = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='dataTitle' and text()='Born']")
            )
        )

        raw_birthplace = browser.execute_script(
            "return arguments[0].nextSibling.textContent.trim();", born_label
        )

        birthplace = re.sub(r"^in\s+", "", raw_birthplace)
    except TimeoutException:
        birthplace = None
    # Returns birthplace and country of birth.
    return birthplace, cleanup_birthplace(birthplace)


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_goodreads_url(user_profile)
    print(books)
