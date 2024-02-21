import pytest
from goodreads_scraper.scrape import scrape_shelf, process_profile
from pathlib import Path

fixture_path = Path(__file__).parent.joinpath("test_assets", "example_goodreads.html")


@pytest.fixture
def goodreads_html():
    # Read the HTML content from the fixture file
    with open(fixture_path, "r", encoding="utf-8") as file:
        return file.read()


TEST_URL = "https://www.goodreads.com/review/list/71341746?shelf=quarantine"


EXPECTED_RESULTS = {
    "number_of_books": 13,
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
    for title in ["Les Visages", "O poderoso chefão"]:
        assert title in actual_titles


@pytest.mark.integration
def test_scrape_another_live_shelf():
    # Run the scraper
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    actual_results = process_profile(user_profile)

    # Check if the number of books matches the expectation
    assert len(actual_results) >= 300

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles


@pytest.mark.integration
def test_scrape_saved_shelf():
    file_uri = fixture_path.resolve().as_uri()

    # Call scrape_shelf with the file URI
    actual_results = scrape_shelf(file_uri)

    # Check if the number of books matches the expectation
    assert len(actual_results) == EXPECTED_RESULTS["number_of_books"]

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles
