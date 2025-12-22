from pathlib import Path
from scraptolib.scrapers.ProfileScraper import ProfileScraper
import json
from scraptolib.utils.helpers import store_json_data

BASE_DIR = Path(__file__).resolve().parent.parent

chromedriver_path = BASE_DIR / "chromedriver.exe"
input_path = BASE_DIR / "scrapers" / "mock_data" / "href_results.json"
output_path = BASE_DIR / "scrapers" / "mock_data" / "profile_results.json"

with open(input_path) as f:
    data = json.load(f)[:2]

scpr = ProfileScraper(
    driver_path=str(chromedriver_path)
)

scpr.start_driver()

results = []
for profile in data:
    profile_data = scpr.run_scraping(
        profile_href=profile['Page_doctolib']
        )
    results += profile_data

store_json_data(
    data=results,
    target_path=output_path
)

scpr.stop_driver()