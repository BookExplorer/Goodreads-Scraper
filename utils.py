from validators.url import url as url_validator
import re


def is_valid_goodreads_url(url: str) -> bool:
    if url_validator(url) and re.match(pattern=r'https?://www\.goodreads\.com/.*', string = url):
        return True
    return False