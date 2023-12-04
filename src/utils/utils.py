from validators.url import url as url_validator
from selenium.webdriver.chrome.webdriver import WebDriver
import re
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse, ParseResult
from selenium.webdriver.remote.webelement import WebElement


def is_valid_goodreads_url(url: str) -> bool:
    """Validates if a URL is a proper URL from the Goodreads website.

    Args:
        url (str): String representing an URL.

    Returns:
        bool: True if it's a valid GR URL, False otherwise.
    """
    if url_validator(url) and re.match(
        pattern=r"https?://www\.goodreads\.com/.*", string=url
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
    # A URL is a profile if it's a valid Goodreads URL and follows the Regex for having user/show/{USER_ID}
    pattern = r"^https:\/\/www\.goodreads\.com\/user\/show\/\d+$"
    return bool(re.match(pattern, url)) and is_valid_goodreads_url(url)


def create_shelf_url(profile_url: str) -> str:
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


def extract_hidden_td(
    browser: WebDriver, element: WebElement, css_selector: str
) -> str:
    hidden_td_element = element.find_element(By.CSS_SELECTOR, css_selector)
    hidden_td_value = browser.execute_script(
        "return arguments[0].textContent.trim();", hidden_td_element
    )
    return hidden_td_value
