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
