from pathlib import Path
from scraptolib.scrapers.CardsScraper import CardsScraper

BASE_DIR = Path(__file__).resolve().parent.parent

output_path = BASE_DIR / "scrapers" / "mock_data" / "href_results.json"

scpr = CardsScraper()

scpr.run_scraping(
    place_input='example_place',  # change it !
    query_input='example_query',  # change it !
    only_href=True,
    target_path=output_path,
)
