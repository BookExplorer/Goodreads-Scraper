from validators import url as url_validator
from selenium.webdriver.chrome.webdriver import WebDriver
import re
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse, ParseResult
from typing import Dict, Tuple, List, Any
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import chromedriver_autoinstaller
import os

# and if it doesn't exist, download it automatically,
# then add chromedriver to path
STARS_ENUM = {
    "did not like it": 1,
    "it was ok": 2,
    "liked it": 3,
    "really liked it": 4,
    "it was amazing": 5,
}


def load_js_file(file_name: str) -> str:
    script_dir = os.path.dirname(__file__)  # Absolute directory the script is in
    abs_file_path = os.path.join(script_dir, file_name)
    with open(abs_file_path, "r") as file:
        return file.read()


def is_valid_goodreads_url(url: str) -> bool:
    """Validates if a URL is a proper URL from the Goodreads website.

    Args:
        url (str): String representing an URL.

    Returns:
        bool: True if it's a valid GR URL, False otherwise.
    """
    if url_validator(url) and re.match(
        pattern=r"https?://www\.goodreads\.com/.*", string=url, flags=re.IGNORECASE
    ):
        return True
    return False


def is_goodreads_profile(url: str) -> bool:
    """Verifies if a provided URL is a proper Goodreads profile URL.
    Calls upon is_valid_goodreads_url for good measure.

    Args:
        url (str): String representing an URL to be checked.

    Returns:
        bool: True if it's a user profile in GR, False otherwise.
    """
    # A URL is a profile if it's a valid Goodreads URL and follows the Regex for having user/show/{USER_ID}-(username)
    pattern = r"^https:\/\/www\.goodreads\.com\/user\/show\/\d+(-\w+)*$"
    return bool(re.match(pattern, url)) and is_valid_goodreads_url(url)


def create_read_shelf_url(profile_url: str) -> str:
    """From a valid GR profile url, get the read shelf URL.
    Although this does work starting from the read shelf itself, it's better to just always use it with the user's profile.
    Some shelves will add the username to the URL itself, making this not ideal to work with. Keep it simple for now.

    Args:
        profile_url (str): A valid GR profile URL.

    Returns:
        str: The URL for that GR user's shelf of read books.
    """
    # Parse the profile URL
    parsed_url = urlparse(profile_url)

    # Construct the path for the read shelf URL
    user_id = parsed_url.path.split("/")[-1]
    new_path = f"/review/list/{user_id}"

    # Construct the new URL
    read_shelf_url = urlunparse(
        ParseResult(
            scheme=parsed_url.scheme,  # Https
            netloc=parsed_url.netloc,  # The goodreads site
            path=new_path,  # The review list for that user
            params="",
            query="shelf=read",
            fragment="",
        )
    )

    return read_shelf_url


def create_read_page(shelf_url: str, page_num: int) -> str:
    """From a user's GR shelf URL, create a URL for the read shelf page.

    Args:
        shelf_url (str): Valid URL for a user's GR shelf.
        page_num (int): _description_

    Returns:
        str: URL for that specific GR shelf page.
    """
    parsed_url = urlparse(shelf_url)
    page_url = urlunparse(
        ParseResult(
            scheme=parsed_url.scheme,  # Https
            netloc=parsed_url.netloc,  # The goodreads site
            path=parsed_url.path,  # The review list for that user
            params="",
            query=f"page={page_num}&shelf=read",
            fragment="",
        )
    )
    return page_url


def extract_hidden_td(
    browser: WebDriver, element: WebElement, css_selector: str
) -> str:
    """Extracts hidden content from an element inside another element in the HTML.
    We use this because the shelf is essentially a bunch of rows of class bookalike review.
    Every row has multiple td.field.field_name classes with that row's info.
    However, some of these are hidden and have nested within them a div.value with none display containing the info.

    Args:
        browser (WebDriver): Browser being used by Selenium to scrape.
        element (WebElement): The actual book element which contains the fields with info.
        css_selector (str): The CSS selector method to find the nested div with hidden info.

    Returns:
        str: The extracted value for that desired field.
    """
    hidden_td_element = element.find_element(By.CSS_SELECTOR, css_selector)
    hidden_td_value = browser.execute_script(
        "return arguments[0].textContent.trim();", hidden_td_element
    )
    return hidden_td_value


def extract_author_id(author_url: str) -> str:
    """Extracts Author ID from GR author URL.

    Args:
        author_url (str): URL from an author in Goodreads.

    Returns:
        str: ID to uniquely identify the author in GR.
    """
    author_path = urlparse(author_url).path
    author_id = author_path.split("/")[-1].split(".")[0]
    return author_id


def extract_num_pages(page_string: str) -> int | None:
    """Parses the webelement with the number of pages in a book into an actual number.

    Args:
        page_string (str): The string extracted from the WebElement with the number of pages.

    Returns:
        Union[int, None]: Number of pages if possible.
    """
    parts = page_string.split()
    for p in parts:
        if p.isdigit():
            return int(p)
    return None


def process_book(browser: WebDriver, book: WebElement) -> Dict[str, Any]:
    """Given a web element from the Goodreads' user's shelf, scrapes the book information and returns a dict.


    Args:
        browser (WebDriver): Browser being used by Selenium to scrape.
        element (WebElement): The actual book element which contains the fields with info.

    Returns:
        Dict[str, any]: Dictionary with that book's fields of interest.
    """
    isbn = extract_hidden_td(browser, book, "td.field.isbn div.value")
    isbn13 = extract_hidden_td(browser, book, "td.field.isbn13 div.value")
    title = book.find_element(By.CSS_SELECTOR, "td.field.title").text
    author_info = book.find_element(By.CSS_SELECTOR, "td.field.author div.value a")
    author_name = (
        author_info.text
    )  # TODO: Get author's name from page. Might be better.
    author_link = author_info.get_attribute("href")
    if author_link:
        author_id = int(extract_author_id(author_link))
    avg_rating = float(
        extract_hidden_td(browser, book, "td.field.avg_rating > div.value")
    )
    user_stars = book.find_element(By.CSS_SELECTOR, "td.field.rating").text
    user_rating = STARS_ENUM.get(user_stars, None)
    pages_string = extract_hidden_td(browser, book, "td.field.num_pages")
    num_pages = extract_num_pages(pages_string)
    publishing_date = extract_hidden_td(browser, book, "td.field.date_pub > div.value")
    started_date = extract_hidden_td(browser, book, "td.field.date_started > div.value")
    finished_date = extract_hidden_td(browser, book, "td.field.date_read > div.value")
    added_date = extract_hidden_td(browser, book, "td.field.date_added > div.value")
    book_dict = {
        "title": title,
        "isbn": isbn,
        "isbn13": isbn13,
        "author_name": author_name,
        "author_id": author_id,
        "author_link": author_link,
        "avg_rating": avg_rating,
        "user_rating": user_rating,
        "num_pages": num_pages,
        "publishing_date": publishing_date,
        "started_date": started_date,
        "finished_date": finished_date,
        "added_date": added_date,
    }
    return book_dict


def parse_infinite_status(infinite_status: WebElement) -> Tuple[int, int]:
    """Every shelf, when opened in the default mode, loads only a few books but has infinite scrolling enabled.
    There is a WebElement inside that page that gives the status of how many books are loaded, as in 30 of 321 loaded.
    This function serves to parse this in order to facilitate scrolling until the shelf is fully loaded.


    Args:
        infinite_status (WebElement): WebElement with the infinite status text.

    Returns:
        Tuple[int, int]: Number of books currently loaded, number of total books in that shelf.
    """
    infinite_status_text = infinite_status.text.split(" ")
    remaining_books = int(infinite_status_text[2])
    current_books = int(infinite_status_text[0])
    return current_books, remaining_books


def setup_browser() -> WebDriver:
    """Handles setup of the browser. For now, it's a Chrome Browser.
    TODO: Perhaps this could be dynamical?

    Returns:
        WebDriver: Headless browser to be used for scraping.
    """

    chromedriver_autoinstaller.install(no_ssl=False)  # Check if the current version of chromedriver exists
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'"
    )

    browser = webdriver.Chrome(options=chrome_options)
    return browser


def read_books(browser: WebDriver):
    books = browser.find_elements(By.CLASS_NAME, "bookalike")
    book_list = [process_book(browser, book) for book in books]
    return book_list


def read_books_fast(browser: WebDriver) -> List[Dict[str, Any]]:
    """Faster version of reading books, invokes a JS script to directly interact with all books at once via Selenium.

    Args:
        browser (WebDriver): Browser being used to scrape.

    Returns:
        List[Dict[str any]]: List of books and their attributes.
    """
    js_code = load_js_file("read_books.js")
    # Execute the script and get all book data in one call
    books_data = browser.execute_script(js_code)

    # Process data further if necessary (e.g., mapping 'user_rating' to your STARS_ENUM)
    for book_data in books_data:
        # Example of converting 'user_rating' based on STARS_ENUM
        # This assumes STARS_ENUM is a dict in your Python code mapping the text to a value
        book_data["user_rating"] = STARS_ENUM.get(book_data["user_rating"], None)

        # Process other fields if necessary

    return books_data


def page_wait(browser: WebDriver) -> WebElement:
    """Waits for the Goodreads page to load and clicks the popup so it disappears.

    Args:
        browser (WebDriver): Browser used for scraping.

    Returns:
        WebElement: Body of the webpage.
    """
    # Wait for initial load
    WebDriverWait(browser, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    body = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    # Clicks to remove login popup.
    login_modal = browser.find_elements(By.CLASS_NAME, "loginModal")
    if login_modal:
        webdriver.ActionChains(browser).move_by_offset(10, 100).click().perform()
    return body


def cleanup_birthplace(birthplace: str | None) -> str | None:
    """Cleans up the birthplace string that comes from Goodreads.

    Args:
        birthplace (str | None): Birthplace scraped from Goodreads.

    Returns:
        str | None: Cleaned up birthplace if applicable, None if birthplace is None.
    """
    if birthplace:
        raw_country = birthplace.split(",")[-1].lstrip()
        if raw_country.startswith("The "):
            return raw_country[4:]
        return raw_country
    return None


def is_goodreads_shelf(url: str) -> bool:
    """Verifies if a provided URL is a proper Goodreads shelf URL.
    Calls upon is_valid_goodreads_url for good measure.

    Args:
        url (str): String representing an URL to be checked.

    Returns:
        bool: True if it's a shelf in GR, False otherwise.
    """
    # A URL is a profile if it's a valid Goodreads URL and follows the Regex for having user/show/{USER_ID}-(username)
    pattern = r"^https:\/\/www\.goodreads\.com\/review\/list\/\d+.*$"
    return bool(re.match(pattern, url)) and is_valid_goodreads_url(url)