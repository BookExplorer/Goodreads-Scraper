import pytest
from src.scraper.scrape import scrape_shelf

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
def test_scrape_shelf():
    # Run the scraper
    actual_results = scrape_shelf(TEST_URL)

    # Check if the number of books matches the expectation
    assert len(actual_results) == EXPECTED_RESULTS["number_of_books"]

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles

    # Add more assertions here as necessary to check other expected details
