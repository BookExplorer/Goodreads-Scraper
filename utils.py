from validators.url import url as url_validator
import re


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
