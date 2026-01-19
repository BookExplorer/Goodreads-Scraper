from selenium.webdriver.chrome.webdriver import WebDriver
from goodreads_scraper.utils import (
    is_valid_goodreads_url,
    is_goodreads_profile,
    create_read_shelf_url,
    extract_hidden_td,
    extract_author_id,
    is_goodreads_shelf,
    setup_browser,
    login
)
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.goodreads.com/book/show/12345", True),
        ("https://www.example.com", False),
        ("not a url", False),
        ("https://www.goodreads.com/user/show/1", True),
        ("https://www.goodreads.com/user/show/300", True),
        ("https://www.goodreads.com/book/show/12345?ref=example", True),
        ("https://www.goodreads.com/user/show/300#section", True),
        ("https://subdomain.goodreads.com/user/show/1", False),
        ("https://www.GoodReads.com/user/show/1", True),
        ("https:/www.goodreads.com/user/show/1", False),
        ("https:// goodreads.com/user/show/1", False),
        ("https://www.goodreads.co/user/show/1", False),
        ("https://www.goodreads.com/user/1", True),
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
        ("https://www.goodreads.com/user/show/1?param=value", False),
        ("https://www.goodreads.com/user/show/", False),
        ("https://www.goodreads.com/user", False),
        ("https://profile.goodreads.com/user/show/1", False),
        ("https://www.goodreads.com/user/show/1#details", False),
        ("https:/www.goodreads.com/user/show/1", False),
        ("https://www.goodreads.com/user/show/1 with space", False),
        ("https://www.goodreads.com/user/show/abc", False),
        ("https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem", True),
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
    assert create_read_shelf_url(profile_url=profile_url) == expected


# Fixture to initialize WebDriver
@pytest.fixture
def chrome_browser():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'"
    )
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


# Test function
def test_extract_hidden_td(chrome_browser: WebDriver):
    # Replace with the actual path to your test HTML file
    current_script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the relative path to the HTML file
    relative_path = os.path.join(current_script_dir, "test_assets/test_page.html")
    # Create the file URL
    file_path = f"file://{relative_path}"
    chrome_browser.get(file_path)

    # Wait for the table to be present
    wait = WebDriverWait(chrome_browser, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    # Find the first 'tr' element in the table
    row = chrome_browser.find_element(By.CSS_SELECTOR, "tr")

    # Call the utility function with the appropriate CSS selector for the hidden 'td'
    hidden_text = extract_hidden_td(chrome_browser, row, "td.hidden")

    # Assert the hidden text is what you expect
    assert hidden_text == "Hidden Text"


@pytest.mark.parametrize(
    "url, expected_id",
    [
        ("https://www.goodreads.com/author/show/12345.J.K.Rowling", "12345"),
        ("https://www.goodreads.com/author/show/67890.George_Orwell", "67890"),
        (
            "https://www.goodreads.com/author/show/13579.Author-Name-With-Dashes",
            "13579",
        ),
        ("https://www.goodreads.com/author/show/24680", "24680"),
    ],
)
def test_extract_author_id(url, expected_id):
    assert extract_author_id(url) == expected_id


def test_browser_setup(chrome_browser: WebDriver):
    assert type(chrome_browser) is type(setup_browser())

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.goodreads.com/book/show/12345", False),
        ("https://www.example.com", False),
        ("not a url", False),
        ("https://www.goodreads.com/user/show/1", False),
        ("https://www.goodreads.com/user/show/300", False),
        ("https://www.goodreads.com/review/list/300?shelf=read", True),
        ("https://www.goodreads.com/user/show/1?param=value", False),
        ("https://www.goodreads.com/user/show/", False),
        ("https://www.goodreads.com/user", False),
        ("https://profile.goodreads.com/user/show/1", False),
        ("https://www.goodreads.com/user/show/1#details", False),
        ("https:/www.goodreads.com/user/show/1", False),
        ("https://www.goodreads.com/user/show/1 with space", False),
        ("https://www.goodreads.com/user/show/abc", False),
        ("https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem", False),
        ("https://www.goodreads.com/review/list/1?shelf=nonfiction", True),
        ("https://www.goodreads.com/review/list/1?page=10&shelf=nonfiction", True),
        ("https://www.goodreads.com/review/list/1", True)
    ],
)
def test_is_goodreads_shelf(url: str, expected: bool
                            ) -> None:
    assert is_goodreads_shelf(url) == expected



def test_login(chrome_browser: WebDriver) -> None:
    WebDriverWait(chrome_browser, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(chrome_browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    login(chrome_browser)
    WebDriverWait(chrome_browser, 300).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert len(chrome_browser.find_elements(By.XPATH, "//button[contains(text(), 'Sign in with email')]")) == 0
    assert len(chrome_browser.find_elements(By.XPATH, "//a[contains(text(), 'My Books')]")) > 0
    # TODO: How can I be sure this still works? What is the certainty I have?