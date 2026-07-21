"""
Standalone script to scrape Doctolib practitioner availabilities
and store results in Supabase.

Accepts a profile URL and time-based parameters via CLI arguments or environment variables.
Stores each slot in the fact_availability table, linked to a fact_scrap run.

Usage:
    python scrape_availability.py --url <PROFILE_URL> [--days 28] [--save-last 14] [--output results.json]

Environment variables:
    SCRAPE_URL                  Practitioner profile or booking URL
    SCRAPE_DAYS                 Number of days to scrape (default: 28)
    ACTUALLY_SAVED_DAYS_END     Number of days to actually store, counting from the end (default: all)
    SCRAPE_OUTPUT               Output file path (default: stdout only)
    SUPABASE_URL                Supabase project URL
    SUPABASE_KEY                Supabase service_role key (secret, bypasses RLS)
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta

from supabase import create_client

from scraptolib.scrapers.AvailabilityScraper import AvailabilityScraper


def get_or_create_practitioner(supabase, profile_url: str, practitioner_name: str) -> int:
    """
    Fetch existing practitioner by profile_url or create a minimal entry.
    Returns the practitioner ID.
    """
    response = (
        supabase.table("dim_practitioner")
        .select("id")
        .eq("profile_url", profile_url)
        .execute()
    )

    if response.data:
        return response.data[0]["id"]

    # Create minimal entry — full profile data can be enriched later by ProfileScraper
    insert_response = (
        supabase.table("dim_practitioner")
        .insert({"name": practitioner_name, "profile_url": profile_url})
        .execute()
    )

    return insert_response.data[0]["id"]


def store_scrap_run(supabase, practitioner_id: int, days: int, save_last: int, status: str) -> int:
    """Insert a fact_scrap row and return its ID."""
    response = (
        supabase.table("fact_scrap")
        .insert({
            "practitioner_id": practitioner_id,
            "days_scraped": days,
            "days_saved": save_last,
            "status": status,
        })
        .execute()
    )

    return response.data[0]["id"]


def filter_days_to_save(result: dict, scrape_days: int, save_last: int) -> list[dict]:
    """
    Filter the scraped days to only keep the last `save_last` days.

    If save_last >= scrape_days, all days are kept.
    Otherwise, only days whose date >= (today + scrape_days - save_last) are kept.
    """
    if save_last >= scrape_days:
        return result["days"]

    cutoff_date = date.today() + timedelta(days=scrape_days - save_last)

    filtered = []
    for day in result["days"]:
        # day["date"] is in "YYYY-MM-DD" format
        try:
            day_date = date.fromisoformat(day["date"])
        except (ValueError, TypeError):
            # If date parsing fails, keep it to be safe
            filtered.append(day)
            continue

        if day_date >= cutoff_date:
            filtered.append(day)

    return filtered


def store_availabilities(supabase, scrap_id: int, days_to_save: list[dict], practitioner_name: str):
    """Insert filtered availability slots from the scraping result."""
    rows = []

    for day in days_to_save:
        for slot in day["slots"]:
            is_substitute = slot["handled_by"] != practitioner_name
            rows.append({
                "scrap_id": scrap_id,
                "datetime": slot["datetime"],
                "handled_by": slot["handled_by"],
                "is_substitute": is_substitute,
            })

    if rows:
        # Insert in batches of 500 to avoid payload limits
        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            supabase.table("fact_availability").insert(batch).execute()

    return len(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Doctolib practitioner availabilities and store in Supabase."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=os.environ.get("SCRAPE_URL"),
        help="Practitioner profile or booking URL.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=int(os.environ.get("SCRAPE_DAYS", "28")),
        help="Number of days to scrape (default: 28).",
    )
    parser.add_argument(
        "--save-last",
        type=int,
        default=int(os.environ.get("ACTUALLY_SAVED_DAYS_END", "0")),
        help="Only save the last N days from the scraped range. 0 = save all (default: 0).",
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

    # If save_last is 0, save everything
    save_last = args.save_last if args.save_last > 0 else args.days

    # Initialize Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("SUPABASE_URL and SUPABASE_KEY env variables are required.", file=sys.stderr)
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    # Run the scraper
    scraper = AvailabilityScraper(headless=True)

    result = scraper.run_scraping(
        availability_url=args.url,
        motive_text=None,
        days=args.days,
    )

    if not result:
        print("No availability data retrieved.", file=sys.stderr)
        sys.exit(1)

    # Filter days to only keep the relevant slice
    days_to_save = filter_days_to_save(result, args.days, save_last)

    print(
        f"Scraped {len(result['days'])} day(s), saving {len(days_to_save)} day(s) "
        f"(last {save_last} days of {args.days})",
        file=sys.stderr,
    )

    # Store in Supabase
    practitioner_name = result["practitioner"]
    practitioner_id = get_or_create_practitioner(supabase, args.url, practitioner_name)

    scrap_id = store_scrap_run(supabase, practitioner_id, args.days, save_last, "success")

    slot_count = store_availabilities(supabase, scrap_id, days_to_save, practitioner_name)

    print(f"Stored {slot_count} slots (scrap_id={scrap_id}, practitioner_id={practitioner_id})", file=sys.stderr)

    # Also output JSON (only saved days)
    output_data = {
        "practitioner": result["practitioner"],
        "days": days_to_save,
        "scrap_timestamp": result["scrap_timestamp"],
    }
    output = json.dumps(output_data, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
