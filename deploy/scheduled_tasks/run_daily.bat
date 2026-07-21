@echo off
cd /d "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"
set SCRAPE_DAYS=14
set ACTUALLY_SAVED_DAYS_END=12
docker compose up --build
