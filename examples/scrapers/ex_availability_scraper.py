from scraptolib.scrapers.AvailabilityScraper import AvailabilityScraper

# Example booking URL — replace with any valid Doctolib booking/availabilities link
availability_url = (
    "https://www.doctolib.fr/osteopathe/longeville-les-saint-avold/fausto-lanzeroti"
    "/booking/availabilities?specialityId=10&telehealth=false"
    "&placeId=practice-158134&motiveIds%5B%5D=2615848"
)

scraper = AvailabilityScraper()

result = scraper.run_scraping(
    availability_url=availability_url,
    motive_text=None,  # auto-select the first motive if prompted
)

if result:
    print(f"Practitioner: {result['practitioner']}")
    print(f"Total slots: {result['total_slots']}")
    print()
    for day in result["days"]:
        print(f"{day['date']} ({day['slot_count']} slot(s))")
        for slot in day["slots"]:
            print(f"  - {slot['time']} — {slot['handled_by']}")
        print()
    print(f"Scraped at: {result['scrap_timestamp']}")
else:
    print("No availability data retrieved.")
