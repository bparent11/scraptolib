# Scraptolib — Daily task
# Runs every 12 hours
# Scrapes 14 days, saves the last 12

$taskName = "ScraptoLib-Daily"
$workDir = "C:\Users\Lenovo\Documents\2-Projets\DataScience\Scraping\scraptolib\deploy"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -Command `"Set-Location '$workDir'; `$env:SCRAPE_DAYS='14'; `$env:ACTUALLY_SAVED_DAYS_END='12'; docker compose up --build`"" `
    -WorkingDirectory $workDir

# Trigger: starts at 00:00, repeats every 12h for 365 days
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At "00:00" `
    -RepetitionInterval (New-TimeSpan -Hours 12) `
    -RepetitionDuration (New-TimeSpan -Days 365)

# Settings matching existing ScraptoLib task
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Days 3) `
    -MultipleInstances IgnoreNew `
    -DeleteExpiredTaskAfter (New-TimeSpan -Days 30)

$settings.RunOnlyIfNetworkAvailable = $false
$settings.RunOnlyIfIdle = $false
$settings.StartWhenAvailable = $false
$settings.RestartCount = 3
$settings.RestartInterval = "PT1M"

# Principal: run as Lenovo, only when logged on, highest privileges
$principal = New-ScheduledTaskPrincipal `
    -UserId "Lenovo" `
    -LogonType S4U `
    -RunLevel Highest

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Scraptolib: scrape 14 days, save last 12, every 12h"

Write-Host "Task '$taskName' registered successfully."
