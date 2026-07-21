# Scraptolib — Daily task
# Runs every 12 hours
# Scrapes 14 days, saves the last 12

$taskName = "ScraptoLib-Daily"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"`$env:SCRAPE_DAYS=14; `$env:ACTUALLY_SAVED_DAYS_END=12; docker compose up --build`"" `
    -WorkingDirectory $workDir

$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At "00:00" `
    -RepetitionInterval (New-TimeSpan -Hours 12) `
    -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Description "Scraptolib: scrape 14 days, save last 12, every 12h"

Write-Host "Task '$taskName' registered successfully."
