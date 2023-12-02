from utils import is_valid_goodreads_url, is_goodreads_profile
import pytest


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.goodreads.com/book/show/12345", True),
        ("https://www.example.com", False),
        ("not a url", False),
        ("https://www.goodreads.com/user/show/1", True),
        ("https://www.goodreads.com/user/show/300", True),
    ],
)
def test_goodreads_url(url: str, expected: bool):
    assert is_valid_goodreads_url(url) == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.goodreads.com/book/show/12345", False),
        ("https://www.example.com", False),
        ("not a url", False),
        ("https://www.goodreads.com/user/show/1", True),
        ("https://www.goodreads.com/user/show/300", True),
        ("https://www.goodreads.com/review/list/300?shelf=read", False),
    ],
)
def test_profile_url(url: str, expected: bool):
    assert is_goodreads_profile(url) == expected
