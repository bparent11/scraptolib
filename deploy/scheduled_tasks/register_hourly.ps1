# Scraptolib — Hourly task
# Runs every 2h30 between 6:00 and 18:00
# Scrapes 2 days, saves all

$taskName = "ScraptoLib-Hourly"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"`$env:SCRAPE_DAYS=2; `$env:ACTUALLY_SAVED_DAYS_END=0; docker compose up --build`"" `
    -WorkingDirectory $workDir

# Trigger: every 2h30 between 6:00 and 18:00
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "06:30"

# Repetition: every 2h30 for 12 hours (6:30, 9:00, 11:30, 14:00, 16:30)
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At "06:30" `
    -RepetitionInterval (New-TimeSpan -Hours 2 -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Hours 12)).Repetition

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Description "Scraptolib: scrape 2 days every 2h30 (6h-18h)"

Write-Host "Task '$taskName' registered successfully."
