# Deploy — AvailabilityScraper

Dockerized deployment of the AvailabilityScraper. Runs headless Chrome inside a container, scrapes a Doctolib practitioner's availability, and stores results in Supabase.

---

## Quick start

### 1. Build the image

```bash
cd deploy
docker build -t scraptolib-availability -f Dockerfile ..
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your values:
```
SCRAPE_URL=https://www.doctolib.fr/osteopathe/mimizan/guilhem-blanc?pid=practice-563603
SCRAPE_DAYS=28
ACTUALLY_SAVED_DAYS_END=0
SUPABASE_URL=https://ihkvibcsdscuvxwfdzmz.supabase.co
SUPABASE_KEY=<your_service_role_key>
```

### 3. Run

```bash
docker compose up --build
```

---

## Parameters

| Parameter | Env variable | Default | Description |
|-----------|--------------|---------|-------------|
| URL | `SCRAPE_URL` | — | Practitioner profile or booking URL (required) |
| Days | `SCRAPE_DAYS` | `28` | Number of days ahead to scrape |
| Save last | `ACTUALLY_SAVED_DAYS_END` | `0` (all) | Only store the last N days from the scraped range |
| Supabase URL | `SUPABASE_URL` | — | Supabase project URL |
| Supabase Key | `SUPABASE_KEY` | — | Supabase service_role key |

### Override on the fly (PowerShell)

```powershell
$env:SCRAPE_DAYS=7; $env:ACTUALLY_SAVED_DAYS_END=0; docker compose up --build
```

This overrides `.env` values for the current session only.

---

## Scheduling (Windows Task Scheduler)

Three PowerShell scripts are provided to register automated scraping tasks at different frequencies.

### How to register the tasks

1. Open **PowerShell as Administrator** (right-click → Run as administrator)
2. Navigate to the project:
   ```powershell
   cd C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib
   ```
3. Run each script:
   ```powershell
   .\deploy\scheduled_tasks\register_hourly.ps1
   .\deploy\scheduled_tasks\register_daily.ps1
   .\deploy\scheduled_tasks\register_weekly.ps1
   ```
4. Open **Task Scheduler** (search "Planificateur de taches" in the Start menu)
5. Click **Task Scheduler Library** in the left panel, press **F5** to refresh
6. You should see `ScraptoLib-Hourly`, `ScraptoLib-Daily`, `ScraptoLib-Weekly`

### Task summary

| Task | Frequency | Scrape | Save | Schedule |
|------|-----------|--------|------|----------|
| `ScraptoLib-Hourly` | Every 1h | 2 days | All | 5:30, 6:30, ..., 17:30 |
| `ScraptoLib-Daily` | Every 12h | 14 days | Last 12 | 00:00, 12:00 |
| `ScraptoLib-Weekly` | Every 24h | 35 days | Last 21 | 03:00 |

### Coverage

| Task | Days covered |
|------|-------------|
| Hourly | J+0 to J+2 |
| Daily | J+3 to J+14 |
| Weekly | J+15 to J+35 |

No gaps — every day in the next 35 days is covered.

### To unregister a task

```powershell
Unregister-ScheduledTask -TaskName "ScraptoLib-Hourly" -Confirm:$false
Unregister-ScheduledTask -TaskName "ScraptoLib-Daily" -Confirm:$false
Unregister-ScheduledTask -TaskName "ScraptoLib-Weekly" -Confirm:$false
```

### Prerequisites

- Docker Desktop must be running (set it to start with Windows)
- The laptop must stay powered on (disable sleep in Power Settings)

---

## Output format

```json
{
  "practitioner": "M. X X",
  "days": [
    {
      "date": "2026-06-22",
      "slots": [
        {"datetime": "2026-06-22 10:00", "handled_by": "M. X X"},
        {"datetime": "2026-06-22 14:00", "handled_by": "Mme Y Y"}
      ]
    }
  ],
  "scrap_timestamp": "2026-06-20 12:30:00"
}
```

- `practitioner`: the person who owns the Doctolib profile
- `handled_by`: who actually ensures each consultation (same as practitioner if no blue dot, otherwise the collaborator's name)

---

## Notes

- The container runs Chrome in headless mode via `undetected-chromedriver`, no display needed.
- The scraper handles cookie banners (including Didomi), motive selection, "Voir plus" buttons, and "Retry later" pages automatically.
- Accepts both profile URLs (`/osteopathe/city/name?pid=...`) and direct booking URLs (`/booking/availabilities?...`).
- Results are stored in Supabase (`fact_scrap` + `fact_availability` tables).
