# Scraptolib — Weekly task
# Runs every 24 hours
# Scrapes 35 days, saves the last 21

$taskName = "ScraptoLib-Weekly"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"`$env:SCRAPE_DAYS=35; `$env:ACTUALLY_SAVED_DAYS_END=21; docker compose up --build`"" `
    -WorkingDirectory $workDir

$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "03:00"

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Description "Scraptolib: scrape 35 days, save last 21, every 24h"

Write-Host "Task '$taskName' registered successfully."
