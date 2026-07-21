@echo off
cd /d "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"
set SCRAPE_DAYS=35
set ACTUALLY_SAVED_DAYS_END=21
docker compose up --build
