from utils.utils import (
    is_valid_goodreads_url,
    is_goodreads_profile,
    create_shelf_url,
    extract_hidden_td,
)
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


@pytest.mark.parametrize(
    "profile_url,expected",
    [
        (
            "https://www.goodreads.com/user/show/1",
            "https://www.goodreads.com/review/list/1?shelf=read",
        ),
        (
            "https://www.goodreads.com/user/show/300",
            "https://www.goodreads.com/review/list/300?shelf=read",
        ),
        (
            "https://www.goodreads.com/user/show/100",
            "https://www.goodreads.com/review/list/100?shelf=read",
        ),
    ],
)
def test_read_shelf_fetch(profile_url: str, expected: str):
    assert create_shelf_url(profile_url=profile_url) == expected


def test_hidden_element_extraction():
    pass
