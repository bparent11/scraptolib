from pathlib import Path
from scraptolib.scrapers.CardsScraper import CardsScraper

BASE_DIR = Path(__file__).resolve().parent.parent

chromedriver_path = BASE_DIR / "chromedriver.exe"
output_path = BASE_DIR / "scrapers" / "mock_data" / "href_results.json"


scpr = CardsScraper(
    driver_path=str(chromedriver_path)
)

scpr.run_scraping(
    place_input='example_place', # change it !
    query_input='example_query', # change it ! 
    only_href=True,
    target_path=output_path
    )