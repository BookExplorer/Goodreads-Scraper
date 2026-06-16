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
    read_books_from_html
)
from goodreads_scraper import auth
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Dict, List, Any
import re
from logger import logger
import time
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import requests
from bs4 import BeautifulSoup
from lxml import etree # type: ignore
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
    """Performs the extraction of all the books from a valid shelf URL."""
    t0 = time.time()
    browser = setup_browser(debug=debug)
    print(f"setup_browser: {time.time()-t0:.2f}s", flush=True)

    t1 = time.time()
    browser.get(url)
    auth.authenticate(browser, url)
    print(f"auth: {time.time()-t1:.2f}s", flush=True)

    t2 = time.time()
    body = page_wait(browser)
    print(f"page_wait: {time.time()-t2:.2f}s", flush=True)

    t3 = time.time()
    try:
        infinite_status = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "infiniteStatus"))
        )
        infinite_status_text = infinite_status.text
    except TimeoutException:
        logger.debug("Infinite status timeout.")
        infinite_status_text = None
    print(f"infinite status wait: {time.time()-t3:.2f}s", flush=True)

    if infinite_status_text:
        t4 = time.time()
        scroll_shelf(infinite_status, body, browser)
        print(f"scroll shelf: {time.time()-t4:.2f}s", flush=True)
        t5 = time.time()
        book_list = read_books_fast(browser)
        print(f"read fast: {time.time()-t5:.2f}s", flush=True)
        browser.quit()
        print(f"total: {time.time()-t0:.2f}s", flush=True)
        return book_list

    t5 = time.time()
    book_list = read_books_fast(browser)
    print(f"read fast (page 1): {time.time()-t5:.2f}s", flush=True)

    try:
        t6 = time.time()
        pagination = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "reviewPagination"))
        )
        next_pages = pagination.find_elements(By.CSS_SELECTOR, "a")
        max_page = int(next_pages[-2].text)
        print(f"find pagination: {time.time()-t6:.2f}s", flush=True)
    except TimeoutException:
        logger.debug("No pagination, single page shelf.")
        browser.quit()
        print(f"total: {time.time()-t0:.2f}s", flush=True)
        return book_list

    t7 = time.time()

    print(f"build session + quit browser: {time.time()-t7:.2f}s", flush=True)
    t8 = time.time()
    read_pages = [create_read_page(url, i) for i in range(2, max_page+1)]
    with FuturesSession(max_workers=8) as session:
        session.headers.update({
        "User-Agent": browser.execute_script("return navigator.userAgent;"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
        for cookie in browser.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])
        browser.quit()
        futures = [session.get(read_page) for read_page in read_pages]
        for future in as_completed(futures):
            response = future.result()
            response.raise_for_status()
            parsed = read_books_from_html(response.text)
            book_list += parsed
    print(f"page loop: {time.time()-t8:.2f}s", flush=True)

    print(f"total: {time.time()-t0:.2f}s", flush=True)
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
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, 'html.parser')
    dom = etree.HTML(str(soup))
    selector = dom.xpath("//div[@class='dataTitle' and text()='Born']/following-sibling::text()")
    if len(selector) > 0:
        raw_birthplace = selector[0].strip()
        birthplace = re.sub(r"^in\s+", "", raw_birthplace)
    else:
        birthplace = None
    return birthplace, cleanup_birthplace(birthplace)


if __name__ == "__main__":
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    books = process_goodreads_url(user_profile)
    print(books)
