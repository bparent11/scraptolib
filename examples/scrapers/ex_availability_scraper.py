from pathlib import Path
import json
from scraptolib.scrapers.AvailabilityScraper import AvailabilityScraper
from scraptolib.utils.helpers import store_json_data

BASE_DIR = Path(__file__).resolve().parent.parent

input_path = BASE_DIR / "scrapers" / "mock_data" / "profile_results.json"
output_path = BASE_DIR / "scrapers" / "mock_data" / "availability_results.json"

with open(input_path) as f:
    data = json.load(f)

# Scrape the first profile's availabilities
profile = data[0]
profile_url = profile["location"][1]

scraper = AvailabilityScraper()

result = scraper.run_scraping(
    availability_url=profile_url,
    motive_text=None,  # auto-select the first motive if prompted
    weeks=1,
)

if result:
    output = {
        "practitioner": result["practitioner"],
        "address": profile["address"],
        "profile_url": profile_url,
        "days": result["days"],
        "scrap_timestamp": result["scrap_timestamp"],
    }

    store_json_data(
        data=[output],
        target_path=str(output_path),
    )

    print(f"Practitioner: {output['practitioner']}")
    print(f"Address: {output['address']}")
    print()
    for day in output["days"]:
        print(f"{day['date']}")
        for slot in day["slots"]:
            print(f"  - {slot['datetime']} — handled by: {slot['handled_by']}")
        print()
    print(f"Scraped at: {output['scrap_timestamp']}")
else:
    print("No availability data retrieved.")
