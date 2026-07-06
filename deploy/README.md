# Deploy — AvailabilityScraper

Dockerized deployment of the AvailabilityScraper. Runs headless Chrome inside a container, scrapes a Doctolib practitioner's availability for a given number of weeks, and outputs the results as JSON.

---

## Quick start

### 1. Build the image

```bash
cd deploy
docker build -t scraptolib-availability -f Dockerfile ..
```

### 2. Run it

Pass the URL and number of weeks directly:

```bash
docker run --rm \
  scraptolib-availability \
  --url "https://www.doctolib.fr/osteopathe/mimizan/guilhem-blanc?pid=practice-563603" \
  --weeks 4
```

The JSON output is printed to stdout.

### 3. Save to a file

Mount a volume and use `--output`:

```bash
docker run --rm \
  -v $(pwd)/output:/app/output \
  scraptolib-availability \
  --url "https://www.doctolib.fr/osteopathe/mimizan/guilhem-blanc?pid=practice-563603" \
  --weeks 4 \
  --output output/results.json
```

The results will be in `./output/results.json` on your host.

---

## Using docker compose

### 1. Create a `.env` file from the example

```bash
cp .env.example .env
```

### 2. Edit `.env` with your target URL and weeks

```
SCRAPE_URL=https://www.doctolib.fr/osteopathe/mimizan/guilhem-blanc?pid=practice-563603
SCRAPE_WEEKS=4
```

### 3. Run

```bash
docker compose up --build
```

Results are saved to `deploy/output/results.json`.

---

## Parameters

| Parameter | CLI flag | Env variable | Default | Description |
|-----------|----------|--------------|---------|-------------|
| URL | `--url` | `SCRAPE_URL` | — | Practitioner profile or booking URL (required) |
| Weeks | `--weeks` | `SCRAPE_WEEKS` | `4` | Number of weeks of availability to scrape |
| Output | `--output` | `SCRAPE_OUTPUT` | stdout | File path to write JSON results |

CLI flags take precedence over environment variables.

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
        {"datetime": "2026-06-22 14:00", "handled_by": "Mme X X"}
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

- The container runs Chrome in headless mode, no display needed.
- Selenium Manager automatically downloads the matching ChromeDriver at build time.
- The scraper handles cookie banners, motive selection, "Voir plus" buttons, and "Retry later" pages automatically.
- Accepts both profile URLs (`/osteopathe/city/name?pid=...`) and direct booking URLs (`/booking/availabilities?...`).
