"""
Standalone script to scrape Doctolib practitioner availabilities.

Accepts a profile URL and number of weeks via CLI arguments or environment variables.
Outputs the result as JSON to stdout and optionally to a file.

Usage:
    python scrape_availability.py --url <PROFILE_URL> [--weeks 4] [--output results.json]

Environment variables (override CLI args):
    SCRAPE_URL      Practitioner profile or booking URL
    SCRAPE_WEEKS    Number of weeks to scrape (default: 4)
    SCRAPE_OUTPUT   Output file path (default: stdout only)
"""

import argparse
import json
import os
import sys

from scraptolib.scrapers.AvailabilityScraper import AvailabilityScraper


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Doctolib practitioner availabilities."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=os.environ.get("SCRAPE_URL"),
        help="Practitioner profile or booking URL.",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=int(os.environ.get("SCRAPE_WEEKS", "4")),
        help="Number of weeks to scrape (default: 4).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.environ.get("SCRAPE_OUTPUT"),
        help="Output JSON file path. If omitted, prints to stdout.",
    )

    args = parser.parse_args()

    if not args.url:
        parser.error("A URL is required. Use --url or set SCRAPE_URL env variable.")

    scraper = AvailabilityScraper(headless=True)

    result = scraper.run_scraping(
        availability_url=args.url,
        motive_text=None,
        weeks=args.weeks,
    )

    if not result:
        print("No availability data retrieved.", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=2, ensure_ascii=False)

    # Always print to stdout
    print(output)

    # Optionally write to file
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nResults saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
