from utils import is_valid_goodreads_url
import pytest
@pytest.mark.parametrize("url,expected", [
    ('https://www.goodreads.com/book/show/12345', True),
    ('https://www.example.com', False),
    ('not a url', False),
    # Add more test cases as needed
])
def test_goodreads_url(url :str, expected: bool):
    assert is_valid_goodreads_url(url) == expected