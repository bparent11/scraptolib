from pathlib import Path
import json
from scraptolib.scrapers.ProfileScraper import ProfileScraper
from scraptolib.utils.helpers import store_json_data

BASE_DIR = Path(__file__).resolve().parent.parent

input_path = BASE_DIR / "scrapers" / "mock_data" / "href_results.json"
output_path = BASE_DIR / "scrapers" / "mock_data" / "profile_results.json"

with open(input_path) as f:
    data = json.load(f)[:2]

scpr = ProfileScraper()

scpr.start_driver()

results = []
for profile in data:
    profile_data = scpr.run_scraping(
        profile_href=profile['Page_doctolib']
    )
    results += profile_data

print(results)

store_json_data(
    data=results,
    target_path=output_path,
)

scpr.stop_driver()
