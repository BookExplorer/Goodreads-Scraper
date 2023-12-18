import pytest
from src.scraper.scrape import scrape_shelf
from pathlib import Path
from urllib.request import pathname2url

# Define the path to your fixture
fixture_path = (
    Path(__file__).parent.joinpath("test_assets", "example_goodreads.html").resolve()
)


@pytest.fixture
def goodreads_html():
    # Read the HTML content from the fixture file
    with open(fixture_path, "r", encoding="utf-8") as file:
        return file.read()


# The known URL you're testing against
TEST_URL = "https://www.goodreads.com/review/list/71341746?shelf=quarantine"

# The expected results, which you have determined beforehand
EXPECTED_RESULTS = {
    "number_of_books": 13,  # Replace with the actual expected number of books
    "known_titles": [
        "Dom Quixote",
        "Iracema",
    ],
}


@pytest.mark.integration
def test_scrape_live_shelf():
    # Run the scraper
    actual_results = scrape_shelf(TEST_URL)

    # Check if the number of books matches the expectation
    assert len(actual_results) == EXPECTED_RESULTS["number_of_books"]

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles


@pytest.mark.integration
def test_scrape_saved_shelf(goodreads_html):
    actual_results = scrape_shelf(pathname2url(str(fixture_path)))

    # Check if the number of books matches the expectation
    assert len(actual_results) == EXPECTED_RESULTS["number_of_books"]

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles
