from mypy.bogus_type import T
import pytest
from typing import Tuple
from goodreads_scraper.scrape import scrape_shelf, process_goodreads_url, scrape_gr_author
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
    actual_results = scrape_shelf(TEST_URL, debug=True)

    # Check if the number of books matches the expectation
    assert len(actual_results) == EXPECTED_RESULTS["number_of_books"]

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]
    for title in EXPECTED_RESULTS["known_titles"]:
        assert title in actual_titles


@pytest.mark.integration
def test_process_profile():
    # Run the scraper
    user_profile = "https://www.goodreads.com/user/show/71341746-tamir-einhorn-salem"
    actual_results = process_goodreads_url(user_profile)

    # Check if the number of books matches the expectation
    assert len(actual_results) >= 300

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]

    for title in ["Les Visages", "O poderoso chefão"]:
        assert title in actual_titles

@pytest.mark.integration
def test_process_profile_with_shelf_url():
    # Run the scraper
    url = "https://www.goodreads.com/review/list/71341746?shelf=read"
    actual_results = process_goodreads_url(url)

    # Check if the number of books matches the expectation
    assert len(actual_results) >= 300

    # Verify that the known titles are in the actual results
    actual_titles = [book["title"] for book in actual_results]

    for title in ["Les Visages", "O poderoso chefão"]:
        assert title in actual_titles

@pytest.mark.integration
def test_process_profile_invalid_url():
    url = "https://www.goodreads.com/book/show/17899167-o-quarto-de-jacob"
    with pytest.raises(ValueError):
        process_goodreads_url(url=url)

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


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.goodreads.com/author/show/13199.Alain_de_Botton",
            ("Zurich, Switzerland", "Switzerland"),
        ),
        ("https://www.goodreads.com/author/show/6062267.Yaniv_Shimony", (None, None)),
    ],
)
def test_scrape_gr_author(url: str, expected: Tuple):
    results = scrape_gr_author(url)
    assert results == expected
